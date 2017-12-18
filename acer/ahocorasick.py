# -*- coding:utf-8 -*-
# Aho-Corasick Algorithm Stack Version
# Author    yanwii

from trie_tree import Trie
import json
import pymysql
import time
import os
import cPickle
import numpy as np

class AhoCorasick():
    def __init__(self):
        self.goto = {}
        self.output = {}
        self.keywords = []
        self.failure = {}
        self.child_status_tree = {}
        self.model_path = "./model/"

        self.base = []
        self.check = []
        self.word_map = {}
        self.index_to_state = {0:0}

        if self.keywords:
            self.make_goto()
            self.make_failure()

    def add_words(self, keywords, make_AC=False):
        for keyword in keywords:
            self.keywords.append(keyword)
        
        if make_AC:
            self.make_AC()
    
    def make_AC(self):
        self.goto = {}
        self.output = {}
        self.failure = {}
        self.failure_tree = {}
        self.child_tree = {}

        self.base = np.zeros(len(self.keywords) + 10)
        self.check = np.zeros(len(self.keywords) + 10)
        self.is_output = np.zeros(len(self.keywords) + 10)
        self.word_map = {}
        self.make_goto()
        self.make_failure()

    def restore(self, path=''):
        model_path = path if path else self.model_path
        try:
            listdir = os.listdir(model_path)
        except OSError,e:
            os.mkdir(model_path)
            listdir = os.listdir(model_path)

        if "model.pkl" in listdir:
            f = open(model_path + "model.pkl")
            model = cPickle.load(f)
            f.close()
        else:
            print("no model")
            model = self
        return model

    def save(self, path=''):
        model_path = path if path else self.model_path
        if self.keywords:
            f = open(model_path+"model.pkl", "wb")
            cPickle.dump(self, f)
            f.close()
    

    def double_array(self):
        self.add_words([u'啊', u'阿根廷', u'阿胶', u'埃及', u'阿拉伯人', u'阿拉伯'], True)
        queue = []
        tree = self.goto['root']
        for i in tree:
            if i != 'status' and i != 'red':
                word = i
                status = tree[i]['status']
                child_tree = tree[i]
                self.word_map[word] = status
                self.index_to_state[status] = status
                queue.append([word, status, child_tree])

        while queue:
            node = queue.pop(0)
            word, status, current_tree = node
            if self.is_end(current_tree):
                map_status = self.word_map.get(word, status)
                self.is_output[map_status] = 1
                continue
            # find base and check
            k = 0
            child_status = [current_tree[i]['status'] for i in current_tree if i != 'status' and i != 'red']
            while True:
                k += 1
                tmp = sum(map(lambda x:self.base[x+k] + self.check[x+k], child_status))
                if tmp == 0:
                    map_status = self.word_map.get(word, status)
                    # tag output
                    if status in self.output:
                        self.is_output[map_status] = 1
                    self.base[map_status] = k
                    for i in current_tree:
                        if i == 'status' or i == 'red':
                            continue
                        child_word = i
                        status = current_tree[i]['status']
                        child_tree = current_tree[i]
                        queue.append([child_word, status, child_tree])
                        self.check[status+k] = map_status
                        self.word_map[child_word] = status+k 
                        self.index_to_state[status] = status + k
                    break
        # loop base
        for i in range(self.is_output.shape[0]):
            if self.is_output[i] == 1:
                if self.base[i] == 0:
                    self.base[i] = -i
                else:
                    self.base[i] = -self.base[i]
        self.base = self.base[1:]
        self.check = self.check[1:]
        self.make_failure_new()

    def make_failure_new(self): 
        start = time.time()

        my_queue = []
        node = [0, "root", self.goto['root']]
        my_queue.append(node)
        while my_queue:
            node = my_queue.pop(0)
            parent_status = node[0]
            word = node[1]
            tree = node[2]
            current_status = tree['status']

            # status tree
            self.child_tree[current_status] = tree

            # failure tree and failure map
            if parent_status == 0:
                self.failure[current_status] = 0
            else:
                # find failure
                parent_failure_status = self.failure[parent_status]
                parent_failure_tree = self.child_tree[parent_failure_status]
                if word in parent_failure_tree:
                    # the child status of the parent failure tree
                    child_status = parent_failure_tree[word]['status']
                    self.failure[current_status] = child_status
                    if child_status in self.output:
                        # fix 
                        if current_status not in self.output:
                            self.output[current_status] = []
                        self.output[current_status].extend(self.output[child_status])

                else:
                    self.failure[current_status] = 0

            for i in tree:
                if i == 'status' or i == 'red':
                    continue
                parent_status = node[2]['status']
                my_queue.append([parent_status, i, node[2][i]])
        stop = time.time()
        print("Make fail table costs {:.2f}".format(stop-start))

        # map to index
        self.fail = {}
        for key,value in self.failure.items():
            key = self.index_to_state.get(key)
            value = self.index_to_state.get(value)
            self.fail[key] = value
        print self.fail

    def make_goto(self):
        start = time.time()
        trie = Trie()
        for word in self.keywords:
            trie.add(word)
        self.goto = trie.tree
        self.goto['root']['status'] = 0
        self.output = trie.output
        stop = time.time()
        #print("Make goto table costs {:.2f}".format(stop-start))

    def make_failure(self):
        start = time.time()

        my_queue = []
        node = [0, "root", self.goto['root'], []]
        my_queue.append(node)
        while my_queue:
            node = my_queue.pop(0)
            parent_status = node[0]
            word = node[1]
            tree = node[2]
            parent_path = node[3]
            current_status = tree['status']

            # status tree
            #self.child_tree[current_status] = tree
            if current_status not in self.child_status_tree:
                self.child_status_tree[current_status] = []
            self.child_status_tree[current_status] += parent_path + [word]

            # failure tree and failure map
            if parent_status == 0:
                self.failure[current_status] = 0
            else:
                # find failure
                parent_failure_status = self.failure[parent_status]

                # change the regular tree to status tree
                parent_failure_tree = self.get_child_tree(parent_failure_status)
                #parent_failure_tree = self.child_tree[parent_failure_status]

                if word in parent_failure_tree:
                    # the child status of the parent failure tree
                    child_status = parent_failure_tree[word]['status']
                    self.failure[current_status] = child_status
                    if child_status in self.output:
                        if current_status not in self.output:
                            self.output[current_status] = []
                        self.output[current_status].extend(self.output[child_status])
                else:
                    self.failure[current_status] = 0

            for i in tree:
                if i == 'status' or i == 'red':
                    continue
                parent_status = node[2]['status']
                my_queue.append([parent_status, i, node[2][i], parent_path+[word]])
        stop = time.time()
        #print("Make fail table costs {:.2f}".format(stop-start))

    def get_child_tree(self, status):
        path = self.child_status_tree[status]
        tree = self.goto
        for status in path:
            tree = tree[status]
        return tree

    def search(self, string):
        my_queue = []
        my_queue.append([string, 0, 0])
        raw_string = string
        output = []
        while my_queue:
            node = my_queue.pop(0)
            string, status, stop = node
            if not string:
                break
            
            # change the regular tree to status tree
            tree = self.get_child_tree(status)
            #tree = self.child_tree[status]
            #print status_tree
            #print tree
            #print "-"*50
            failure_status = self.failure[status]

            #print string
            #print status
            #print failure_status
            #print tree
            
            word = string[0]
            if word in tree:
                status = tree[word]['status']
                my_queue.append([string[1:], status, stop+1])

                # check output
                if status in self.output:
                    for word in self.output[status]:
                        start = stop - len(word) + 1
                        #print "Found word %s start %s stop %s dev %s" % (word,start,stop,raw_string[start:stop+1])                        
                        output.append({
                            "word":word,
                            "start":start,
                            "stop":stop+1
                        })
            elif failure_status or status !=0:
                status = failure_status
                my_queue.append([string, failure_status, stop])
            else:
                my_queue.append([string[1:], 0, stop+1])

        return {"result":output}

    def is_end(self, tree):
        if tree.keys() == ['status', 'red'] or tree.keys() == ['red', 'status']:
            return True
        else:
            return False

if __name__ == "__main__":
    ac = AhoCorasick()
    ac.double_array()