# -*- coding:utf-8 -*-
# Aho-Corasick Algorithm Stack Version
# Author    yanwii

from trie_tree import Trie
import json
import pymysql
import time
import os
import cPickle

class AhoCorasick():
    def __init__(self):
        self.goto = {}
        self.output = {}
        self.keywords = []
        self.child_tree = {}
        self.failure = {}
        self.model_path = "./model/"
        
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
        #print("Make fail table costs {:.2f}".format(stop-start))


    def search(self, string):
        my_queue = []
        my_queue.append([string, 0, 0])
        raw_string = string
        output = []
        while my_queue:
            node = my_queue.pop(0)
            string, status,stop = node
            if not string:
                break
            
            tree = self.child_tree[status]
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


if __name__ == "__main__":
    ac = AhoCorasick()
    print ac.failure