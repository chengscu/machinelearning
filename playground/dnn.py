"""An Example of a DNNClassifier for the Iris dataset.
To run the program, open three shells, each execute the following:
python ./dnn.py --role=chief --index=0
python ./dnn.py --role=worker --index=0
python ./dnn.py --role=worker --index=1
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import argparse
import tensorflow as tf

CSV_COLUMN_NAMES = ['SepalLength', 'SepalWidth',
                    'PetalLength', 'PetalWidth', 'Species']
CSV_TYPES = [[0.0], [0.0], [0.0], [0.0], [0]]

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=10000, type=int,
                    help='number of training steps')
parser.add_argument('--role', type=str, help='role')  # chief, worker
parser.add_argument('--index', type=int, help='role index')

# Download this file from:
# http://download.tensorflow.org/data/iris_training.csv
train_path = '/tmp/iris_training.csv'


def _parse_line(line):
  # Decode the line into its fields
  fields = tf.decode_csv(line, record_defaults=CSV_TYPES)
  
  # Pack the result into a dictionary
  features = dict(zip(CSV_COLUMN_NAMES, fields))
  
  # Separate the label from the features
  label = features.pop('Species')
  
  return features, label


def _csv_input_fn(csv_path, batch_size, training):
  # Create a dataset containing the text lines.
  dataset = tf.data.TextLineDataset(csv_path).skip(1)
  
  # Parse each line.
  dataset = dataset.map(_parse_line)
  
  if training:
    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)
  else:
    dataset = dataset.batch(batch_size)
  
  # Return the dataset.
  return dataset


def _set_tf_logging(logfile, level=tf.logging.INFO):
  import logging
  # get TF logger
  log = logging.getLogger('tensorflow')
  log.setLevel(level)
  
  # create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  
  # create file handler which logs even debug messages
  fh = logging.FileHandler(logfile)
  fh.setLevel(level)
  fh.setFormatter(formatter)
  log.addHandler(fh)


def main(argv):
  args = parser.parse_args(argv[1:])
  
  # Feature columns describe how to use the input.
  my_feature_columns = []
  for key in CSV_COLUMN_NAMES[0:4]:
    my_feature_columns.append(tf.feature_column.numeric_column(key=key))
  
  cluster = {'chief': ['localhost:2220'],
             'worker': ['localhost:2221', 'localhost:2222']}
  
  os.environ['TF_CONFIG'] = json.dumps({
    'cluster': cluster,
    'task': {'type': args.role, 'index': args.index}
  })
  
  dist_strategy = tf.contrib.distribute.CollectiveAllReduceStrategy()
  run_config = tf.estimator.RunConfig(train_distribute=dist_strategy,
                                      eval_distribute=dist_strategy,
                                      save_checkpoints_secs=10,
                                      keep_checkpoint_max=2)
  
  work_dir = '/tmp/iris-{}-{}'.format(args.role, args.index)
  model_dir = os.path.join(work_dir, 'checkpoint')
  export_dir = os.path.join(work_dir, 'model')
  log_file = os.path.join(work_dir, 'train.log')
  if not os.path.exists(work_dir):
    os.makedirs(work_dir)
  _set_tf_logging(log_file)
  
  # Build 2 hidden layer DNN with 10, 10 units respectively.
  classifier = tf.estimator.DNNClassifier(
    model_dir=model_dir,
    feature_columns=my_feature_columns,
    # Two hidden layers of 10 nodes each.
    hidden_units=[10, 10],
    # The model must choose between 3 classes.
    n_classes=3,
    # Specify run config
    config=run_config
  )
  
  train_spec = tf.estimator.TrainSpec(
    input_fn=lambda: _csv_input_fn(train_path, args.batch_size, True),
    max_steps=args.train_steps,
    hooks=[])
  eval_spec = tf.estimator.EvalSpec(
    input_fn=lambda: _csv_input_fn(train_path, args.batch_size, True))
  tf.estimator.train_and_evaluate(classifier, train_spec, eval_spec)
  
  # Export the model
  def serving_input_receiver_fn():
    """An input_fn that expects a csv row."""
    csv_example = tf.placeholder(
      dtype=tf.string,
      name='input_example')
    receiver_tensors = {'csv_example': csv_example}
    fields = tf.decode_csv(csv_example, record_defaults=CSV_TYPES[0:4])
    features = dict(zip(CSV_COLUMN_NAMES[0:4], fields))
    return tf.estimator.export.ServingInputReceiver(features, receiver_tensors)
  
  if args.role == 'chief' and args.index == 0:
    classifier.export_savedmodel(export_dir, serving_input_receiver_fn, strip_default_attrs=True)


if __name__ == '__main__':
  tf.app.run(main)
