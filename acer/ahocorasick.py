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
        self.vocab = {}
        self.child_status_tree = {}
        self.model_path = "./model/"

        self.base = []
        self.check = []
        self.word_map = []
        self.status_to_index = {0:0}

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

        self.base = np.zeros(len(self.keywords) + 30, dtype=int)
        self.check = np.zeros(len(self.keywords) + 30, dtype=int)
        self.is_output = np.zeros(len(self.keywords) + 30, dtype=int)
        self.word_map = [0] * (len(self.keywords) + 30)
        self.make_goto()
        #self.make_failure()

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
        self.add_words(["he", "sh", "his", "hi", "hsss", "hiss"], True)
        queue = []
        self.base[0] = 1
        queue.append(['root', 0, self.goto['root'], 0])

        while queue:
            node = queue.pop(0)
            word, status, tree, pre_index = node
            child_status = [tree[i]['status'] for i in tree if i != 'status']
            k = 0
            while True:
                k += 1
                tmp = sum(map(lambda x: self.check[x+k], child_status))
                if tmp == 0:
                    for i in tree:
                        if i=='status':
                            continue
                        char = i
                        char_status = tree[i]['status']
                        char_index = char_status + k
                        
                        self.check[char_index] = k
                        self.word_map[char_index] = char

                        self.base[pre_index] = k
                        if i == "end":
                            self.base[char_index] = -1
                            
                        child_tree = tree[i]
                        child_status = tree[i]['status']
                        queue.insert(0, [i, child_status, child_tree, char_index])
                    break
        print json.dumps(self.vocab, indent=2, ensure_ascii=False)
        print self.check
        print self.base
        print self.word_map
        print self.sub_search("hiss")

    def sub_search(self, string):
        '''
            前缀查询
        '''
        queue = []
        queue.append([string, 1, ''])
        result = []
        while queue:
            q = queue.pop(0)
            string, pre_bp ,seg = q
            char = string[0]
            seg += string[0]

            char_index = self.vocab.get(char, -1)
            p = pre_bp + char_index
            bp = self.base[p]
            bbp = self.base[bp]
            cbp = self.check[bp]
            print bp, bbp, cbp
            if bbp == -1 and (bp == cbp):
                result.append(seg)
            if len(string) == 1:
                break
            if string[1:]:
                queue.append([string[1:], bp, seg])
        return result

    def make_goto(self):
        start = time.time()
        trie = Trie()
        for word in self.keywords:
            trie.add(word)
        self.goto = trie.tree
        self.goto['root']['status'] = 0
        self.output = trie.output
        self.vocab = trie.vocab
        stop = time.time()
        #print("Make goto table costs {:.2f}".format(stop-start))

    def make_failure(self):
        queue = []
        for i in self.goto['root']:
            if i == 'status':
                continue
            char = i
            tree = self.goto['root'][i]
            char_index = self.vocab.get(i)
            char_status = tree['status']
            queue.append([char_index, 1])





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
        if tree['status'] == -1:
            return True
        else:
            return False

if __name__ == "__main__":
    ac = AhoCorasick()
    ac.double_array()