# CM-I

### 文件说明

* `未处理数据` - 未处理的原始数据，大多为Office格式
* `粗处理数据` - 粗处理的数据，多为`csv`或`json`格式，经过了初步的关键词提取与结构化
* `药材三元组` - 药材一侧相关关键词及网络数据
* `database` - 提取出的关键词与方剂一侧的关系网络数据
* `graph` - 融合后的关系网络数据 - [具体说明](graph/README.md)
* `lib` - 一些python库
  - `utils.py` - 一些辅助字符串处理的函数
  - `transh.py` - TransH[^1]的一个实现

[^1]: Zhen Wang, Jianwen Zhang et al. *Knowledge Graph Embedding by Translating on Hyperplanes*. AAAI 2014.
