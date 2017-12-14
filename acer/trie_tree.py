# -*- coding:utf-8 -*-
# Trie tree
# Author    yanwii
# Date      2017.12.03 

import json

class Trie:
    def __init__(self):
        self.tree = {
            "root":{},
            }
        self.status = 1
        self.output = {}

    def add(self, word):
        branch = self.tree["root"]
        for index,i in enumerate(word):
            if i not in branch:
                branch[i] = {}
                branch[i]['status'] = self.status
                self.status += 1
            branch = branch[i]
        branch['red'] = -1
        if branch['status'] not in self.output:
            self.output[branch['status']] = []
        if word not in self.output[branch['status']]:
            self.output[branch['status']].append(word)

    def find(self, word):
        branch = self.tree["root"]
        for index,i in enumerate(word):
            if i not in branch:
                return False
            branch = branch[i]
        return 'red' in branch

if __name__ == "__main__":
    trie = Trie()
    trie.add("Hello")
    trie.add("Helloo")

    print(trie.find("Hello"))