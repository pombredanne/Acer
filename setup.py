from distutils.core import setup
  
setup(  
    name = "acer",  
    version = "0.1.3",  
    keywords = ("AhoCorasick", "Aho-Corasick", "Entities matching"),  
    description = "Aho-Corasick algorithm for python",  
    long_description = "Aho-Corasick by Paper:https://pdfs.semanticscholar.org/3547/ac839d02f6efe3f6f76a8289738a22528442.pdf \
                        Reference:https://www.cs.uku.fi/~kilpelai/BSA05/lectures/slides04.pdf	",  
    license = "MIT Licence",  
    url = "https://github.com/yanwii/Aho-Corasick",  
    author = "yanwii",  
    author_email = "yanwii@outlook.com",
    packages_dir = {"", "acer"},
    packages = ['acer'],  
    platforms = "any",  
    scripts = [],  
    requires = ["requests"] 
)