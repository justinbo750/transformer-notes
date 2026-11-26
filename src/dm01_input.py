"""
演示transformer的输入和位置编码
    包括：
        1、词嵌入层（word embedding）
        2、位置编码层（position encoding）

"""

#导包
import torch
import torch.nn as nn
import numpy as np
import math
import matplotlib.pyplot as plt


class Embeddings(nn.Module):
    def __init__(self,vocab_size,d_model):
    #vocab_size:词典大小，即去重后的单词个数   d_model:向量维度，表示词向量维度
        super().__init__()
        #定义变量
        self.vocab_size = vocab_size
        self.d_model = d_model

        #定义词嵌入层，将单词索引（不是单词本身）转换为词向量
        self.embed = nn.Embedding(vocab_size,d_model)

    #前向传播函数
    def forward(self,x):
        return self.embed(x) * math.sqrt(self.d_model)
        #将输入的单词索引转换为词向量，并乘以sqrt(d_model)，进行缩放，避免梯度消失和梯度爆炸



#todo:测试Embedding
def test_Embedding():
    vocab_size,d_model = 1000,512

    #定义词索引
    x = torch.tensor([
        [1,2,3,4,5]
        ,[6,7,8,9,10]
    ])

    #定义词嵌入层
    my_embed = Embeddings(vocab_size,d_model)
    y = my_embed(x)
    print(f'y:{y},y.shape:{y.shape}')   #y.shape:torch.Size([2, 5, 512])


#todo:位置编码层
class PositionalEncoding(nn.Module):
    def __init__(self,d_model,dropout,max_len=50):
        #parameters1:词向量的维度，即d_model
        #parameters2:dropout率，防止过拟合
        #parameters3:最大句子长度，默认为5000
        super().__init__()

        self.dropout = nn.Dropout(p=dropout)
        #定义pe，用来保存位置编码结果
        pe = torch.zeros(max_len,d_model)      #shape为(max_len,d_model)
        #生成大小为(max_len,d_model)的全零张量

        #定义pos，用来保存位置信息
        pos = torch.arange(0,max_len).unsqueeze(1)      #shape为(max_len,1)
        #根据公式逐步复现pe
        # 公式为1/(10000^(2i/d_model)),经过log和exp转变为乘法，又因为取倒数，所以ln要乘以-1
        #torch.arange(0,d_model,2)生成从0到d_model的偶数序列,满足公式中的2i
        #-math.log表示取对数，并添加负号
        div_term = torch.exp(torch.arange(0,d_model,2) * (-math.log(10000.0) / d_model))

        #对pe赋值(偶数列)
        pe[:,0::2] = torch.sin(pos * div_term)
        #对pe赋值(奇数列)
        pe[:,1::2] = torch.cos(pos * div_term)
        # print(f'pe.shape:{pe.shape},pe:{pe}')  #shape:[max_len,d_model]

        # 对pe进行升维，保证后面可以和x进行相加
        pe = pe.unsqueeze(0)

        # 将pe转换为不可训练的张量,防止迭代器更新
        self.register_buffer('pe',pe)



    def forward(self,x):

        #x的形状一定和pe的形状相同，即[batch_size,seq_len,d_model]
        #将词向量和位置编码相加,:表示取所有,x.size(1)表示最大不超过x的第二个维度，即句子长度
        #所以必须满足max_len>=seq_len
        x = x + self.pe[:,:x.size(1),:]
        print(f'x.shape:{x.shape},x:{x}')   #x.shape:torch.Size([2, 5, 512])
        print(f'pe.shape:{self.pe.shape},pe:{self.pe}')   #pe.shape:torch.Size([1, 50, 512])
        #todo:这里可以直接相加是因为pe进行了切割，
        # 从原先的50变成了5，
        # 然后又因为前面刚好是1，
        # 所以可以以利用python的广播机制（各个维度的数字要么相等，要么数字是1，其他情况都会报错）

        return self.dropout(x)

#todo:测试位置编码层
def test_PositionalEncoding():
    vocab_size, d_model, dropout = 1000, 512, 0.5

    x = torch.tensor([
        [1,2,3,4,5]
        ,[6,7,8,9,10]
    ])
    my_embed = Embeddings(vocab_size, d_model)
    y = my_embed(x)
    my_pos = PositionalEncoding(d_model,dropout)
    y = my_pos(y)
    print(f'y:{y},y.shape:{y.shape}')   #y.shape:torch.Size([2, 5, 512])
    return y






#todo:注意力机制
#计算公式：Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V
def attention(query,key,value,mask=None,dropout=None):
    """
    :param query: 查询张量，形状为[batch_size,seq_len,d_model]
    :param key: 键张量，形状为[batch_size,seq_len,d_model]
    :param value: 值张量，形状为[batch_size,seq_len,d_model]
    :param mask: 掩码张量，形状一般和attension_scores(注意力权重)相同，[seq_len,seq_len],后续需要升维
    :param dropout:随机失活
    """
    d_k = query.size(-1)   #d_k为query的最后一个维度，即d_model(词向量维度)
    attention_scores = torch.matmul(query,key.transpose(-2,-1)) / math.sqrt(d_k)
    print(f'attention_scores.shape:{attention_scores.shape}')
    if mask is not None:
        mask = mask.unsqueeze(0)
        attention_scores = attention_scores.masked_fill(mask==0,-1e9)
    #计算注意力权重
    attention_weights = torch.softmax(attention_scores,dim=-1)

    if dropout is not None:
        attention_weights = dropout(attention_weights)

    return torch.matmul(attention_weights,value), attention_weights





#todo:测试注意力机制
def test_attention():
    position_x = test_PositionalEncoding()
    query =key = value= position_x
    dropout_layer = nn.Dropout(p=0.5)
    attension, attention_weights = attention(query,key,value,dropout=dropout_layer)
    print(f'attension:{attension},attension.shape:{attension.shape}')
    print(f'attention_weights:{attention_weights},attention_weights.shape:{attention_weights.shape}')







if __name__ == '__main__':
    test_Embedding()
    test_PositionalEncoding()
    test_attention()

