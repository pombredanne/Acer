# Aho-corasick Algorithm

# 安装
        sudo pip2 install acer
        or 
        pip2 --user install acer
---

# 用法

### 一般用法
        from acer import Acer
        ac = Acer()
        
        # 添加词语
        ac.add_words(["he", "hers", "she", "his", "is"])
        ac.make_AC()

        # or 
        ac.add_words(["he", "hers", "she", "his", "is"], make_AC=True)

        # 搜索
        result = json.dumps(ac.search("ushersis"), indent=2, ensure_ascii=False)

        # 结果
        {
            "result": [
              {
                "start": 1,
                "word": "she",
                "stop": 4
              },
              {
                "start": 6,
                "word": "is",
                "stop": 8
              },
              {
                "start": 2,
                "word": "hers",
                "stop": 6
              },
              {
                "start": 2,
                "word": "he",
                "stop": 4
              }
            ]
        }

