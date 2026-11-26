from dm03_NormandAdd import *
"""
演示编码器层
        具体流程：
        1、输入嵌入层
        2、位置编码
        3、多头自注意力
        4、层归一化和残差连接
        5、前馈网络
        6、层归一化和残差连接
"""

#todo:初始化编码器层
class Encoderlayer(nn.Module):
    def __init__(self,d_model,self_attn,feed_forward,dropout=0.5):
        """
        :param d_model: 词嵌入维度，即词向量维度
        :param self_attn: 多头注意力机制子层
        :param feed_forward: 前馈全连接层FNN
        :param dropout: 随机失活
        """
        super().__init__()
        self.d_model = d_model
        self.self_attn = self_attn
        self.feed_forward = feed_forward

        #一个编码器层含有两个子层，因此需要克隆两个子层对象,返回的是一个可迭代列表，包括[子层对象1，子层对象2]
        self.sublayer = clones(SublayerConnection(size=self.d_model,dropout = dropout),2)

    #定义前向传播
    def forward(self,x,mask):
        #第一层子层连接->多头注意力子层
        x = self.sublayer[0](x,lambda x:self.self_attn(x,x,x,mask))
        #第二层子层连接->前馈全连接层
        x= self.sublayer[1](x,lambda x : self.feed_forward(x))
        return x

#todo:测试编码器层
def testEncoder_layer():
    x = test_PositionalEncoding()
    #实例化子层
    multi_head = MultiHeadedAttention(head = 8,embeded_dim = 512,seq_len = x.size(1),dropout = 0.5)
    feed_forward = FeedForward(d_model = 512 ,d_ff = 1024)
    #创建编码器层
    encoder_layer = Encoderlayer(d_model=512,self_attn=multi_head,feed_forward=feed_forward)
    #创建掩码张量,形状为[head,seq_len,seq_len]
    mask = torch.zeros(8,5,5)
    result = encoder_layer(x,mask=mask)
    print(f'result:{result}')
    print(f'result,shape:{result.shape}')
    print(f'编码器对象：\n{encoder_layer}')




#todo:定义编码器
class Encoder(nn.Module):
    def __init__(self,layer,N):
        super().__init__()
        #layer:单个编码器层，N：编码器层数
        #克隆N个编码器层对象
        self.layers = clones(layer,N)
        self.norm = LayerNorm(layer.d_model)


    def forward(self,x,mask):
        """
        :param x: 输入数据，形状为[seq_len,batch_size,embeded_dim]
        :param mask: 掩码张量，形状为[head,seq_len,seq_len]
        """
        for layer in self.layers:
            x = layer(x,mask)
        return self.norm(x)

#todo:测试编码器
def test_Encoder():
    x = test_PositionalEncoding()
    #实例化子层
    multi_head = MultiHeadedAttention(head = 8,embeded_dim = 512,seq_len = x.size(1),dropout = 0.5)
    feed_forward = FeedForward(d_model = 512 ,d_ff = 1024)
    encoder = Encoder(Encoderlayer(d_model=512,self_attn=multi_head,feed_forward=feed_forward),N=6)
    mask = torch.zeros(8,5,5)
    encoder_result = encoder(x,mask)
    print(f'encoder_result.shape:{encoder_result.shape}')
    print(f'编码器对象：\n{encoder}')
    
    return encoder_result


if __name__ == '__main__':
    # testEncoder_layer()
    test_Encoder()
