from sympy import Lambda

from dm02_selfattension import *

#todo :定义规范化层
class LayerNorm(nn.Module):
    def __init__(self, features, eps=1e-6):
        """
        :param features: 词向量维度
        :param eps: 一个很小的数，防止分母为0
        """
        super().__init__()
        #a的作用是缩放标准化后的结果,初始化为1
        self.a = nn.Parameter(torch.ones(features))
        #b的作用是平移标准化后的结果,初始化为0
        self.b = nn.Parameter(torch.zeros(features))
        self.eps = eps

    def forward(self,x):
        # x的shape是[batch_size,seq_len,d_model]->[2,5,512]
        #计算最后一维的均值和方差
        x_mean =x.mean(-1,keepdim = True)   #x_mean的形状是[2,5,1]
        x_std = x.std(-1,keepdim = True)    #x_std的形状也是[2,5,1]
        return self.a *(x - x_mean)/(x_std +self.eps) +self.b

#todo :测试规范化层
def use_layer_norm():
    #先拿到输入
    x = use_feedforward()
    #定义规范化层
    layer_norm = LayerNorm(features = 512)
    #进行规范化处理
    result = layer_norm(x)
    print(f'result.shape:{result.shape}')
    return result


#batch_norm  和  layer_norm 的区别
#batch_norm针对   同一个特征，不同的样本  进行标准化，一般用于处理图片
#layer_norm针对  同一个样本，不同的特征   进行标准化，一般用于处理序列数据


#todo :定义残差连接和子层
class SublayerConnection(nn.Module):
    def __init__(self,size,dropout):
        super().__init__()
        self.norm = LayerNorm(features=size)
        self.dropout = nn.Dropout(p=dropout)
    def forward(self,x,sublayer):
        """
        :param sublayer:输入的子层，例如多头自注意力子层或前馈神经网络子层
        :param x:输入张量，形状为[batch_size,seq_len,d_model]
        """
        result = x + self.dropout(self.norm(sublayer(x)))
        return result

#todo :测试残差连接和子层
def use_sublayer():
    x = test_PositionalEncoding()
    sublayer_conn = SublayerConnection(size = 512,dropout=0.5)
    result = sublayer_conn(
        x,sublayer = lambda x : MultiHeadedAttention(head = 8 ,embeded_dim= 512,seq_len = 5,dropout=0.5)
        (x,x,x))
    # result = sublayer_conn(x,sublayer = lambda x : FeedForward(d_model=512,d_ff=1024,dropout_p=0.5)(x))
    print(f'result.shape:{result.shape}')




if __name__ == '__main__':
    # use_layer_norm()
    use_sublayer()
