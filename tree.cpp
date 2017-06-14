#include <iostream>
#include <vector>
#include <stdio.h>
#include <stack>
#include <queue>
using namespace std;

struct Node {
	int val = -1;
	Node *pl = nullptr;
	Node *pr = nullptr;
	Node(int val):val(val){};
};

Node* constructTree() {
	int n = 9;
	vector<Node*> nodes(n);
	for(int i = 0; i < n; i++)
		nodes[i] = new Node(i+1);
	for(int i = 0; i < n; i++) {
		int lc = i * 2 + 1;
		int rc = i * 2 + 2;
		if(lc < n) nodes[i]->pl = nodes[lc];
		if(rc < n) nodes[i]->pr = nodes[rc];
	}
	return nodes[0];
}

void bfs(Node *root) {
	if(root == nullptr) return;

	queue<Node*> queue;
	printf("%d ", root->val);
	if(root->pl != nullptr) queue.push(root->pl);
	if(root->pr != nullptr) queue.push(root->pr);

	while(!queue.empty()) {
		Node *n = queue.front();
		printf("%d ", n->val);
		queue.pop();
		if(n->pl != nullptr) queue.push(n->pl);
		if(n->pr != nullptr) queue.push(n->pr);
	}
}

void dfs(Node *root) {
	if(root == nullptr) return;
	printf("%d ", root->val);

	if(root->pl != nullptr) dfs(root->pl);
	if(root->pr != nullptr) dfs(root->pr);
}

void preOrder(Node *root) {
	if(root == nullptr) return;
	printf("%d ", root->val);
	preOrder(root->pl);
	preOrder(root->pr);
}

void preOrderNonRecursive(Node *root) {
	if(root == nullptr) return;

	stack<Node*> stack;
	printf("%d ", root->val);
	if(root->pr != nullptr) stack.push(root->pr);
	if(root->pl != nullptr) stack.push(root->pl);

	while(!stack.empty()) {
		Node *n = stack.top();
		printf("%d ", n->val);
		stack.pop();
		if(n->pr != nullptr) stack.push(n->pr);
		if(n->pl != nullptr) stack.push(n->pl);
	}
}

void inOrder(Node *root) {
	if(root == nullptr) return;
	inOrder(root->pl);
	printf("%d ", root->val);
	inOrder(root->pr);
}

void inOrderNonRecursive(Node *root) {
	if(root == nullptr) return;

	stack<pair<Node*,int>> stack;
	stack.push(make_pair(root, 0));

	while(!stack.empty()) {
		Node *n = stack.top().first;
		if(stack.top().second == 0) {
			stack.top().second = 1;
			if(n->pl != nullptr) stack.push(make_pair(n->pl, 0));
		}
		else if(stack.top().second == 1) {
			printf("%d ", n->val);
			stack.pop();
			if(n->pr != nullptr) stack.push(make_pair(n->pr, 0));
		}
	}
}

void inOrderNonRecursive2(Node *root) {
	if(root == nullptr) return;

	// the top element at the stack is the one that are ready
	// to visit and pop
	stack<Node*> stack;

	// push all the left
	Node *p = root;
	while(p) {
		stack.push(p);
		p = p->pl;
	}

	while(!stack.empty()) {
		Node *n = stack.top();
		printf("%d ", n->val);
		stack.pop();

		// push the right child and all its left
		p = n->pr;
		while(p) {
			stack.push(p);
			p = p->pl;
		}
	}
}

void postOrder(Node *root) {
	if(root == nullptr) return;
	postOrder(root->pl);
	postOrder(root->pr);
	printf("%d ", root->val);
}

void postOrderNonRecursive(Node *root) {
	if(root == nullptr) return;

	stack<pair<Node*,int>> stack;
	stack.push(make_pair(root, 0));

	while(!stack.empty()) {
		Node *n = stack.top().first;
		if(stack.top().second == 0) {
			stack.top().second = 1;
			if(n->pl != nullptr) stack.push(make_pair(n->pl, 0));
		}
		else if(stack.top().second == 1) {
			stack.top().second = 2;
			if(n->pr != nullptr) stack.push(make_pair(n->pr, 0));
		}
		else if(stack.top().second == 2) {
			printf("%d ", n->val);
			stack.pop();
		}
	}
}

int
main() {
	Node* tree = constructTree();
	bfs(tree); printf("\n");
	dfs(tree); printf("\n");
	preOrder(tree); printf("\n");
	preOrderNonRecursive(tree); printf("\n");
	inOrder(tree); printf("\n");
	inOrderNonRecursive(tree); printf("\n");
	inOrderNonRecursive2(tree); printf("\n");
	postOrder(tree); printf("\n");
	postOrderNonRecursive(tree); printf("\n");
	return 0;
}
			
