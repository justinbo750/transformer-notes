"""
演示解码器层


解码器层包含三个子层：
1、掩码多头注意力子层
    层归一化和残差连接
2、多头注意力子层
    层归一化和残差连接
3、前馈全连接层
    层归一化和残差连接
"""


from dm04_Encoderlayer import *
import copy
import torch.nn.functional as F



#todo:定义解码器层
class Decoderlayer(nn.Module):
    def __init__(self, d_model, self_attn, src_attn, feed_forward, dropout=0.5):
        """
        :param d_model: 词嵌入维度，即词向量维度
        :param self_attn: 自注意力机制子层，处理解码器内部的自注意力机制
        :param src_attn: 源注意力机制子层，处理解码器与编码器之间的注意力机制
        :param feed_forward: 前馈全连接层
        :param dropout: 随机失活
        """
        super().__init__()
        # 定义属性
        self.d_model = d_model
        self.self_attn = self_attn
        self.src_attn = src_attn
        self.feed_forward = feed_forward
        self.sublayer = clones(SublayerConnection(size=d_model, dropout=dropout), 3)

    def forward(self, x, encoder_output, source_mask, target_mask):
        """
        :param x: 解码器输入的词嵌入向量
        :param encoder_output: 编码器的输出
        :param source_mask: 源语言的掩码，用于编码器、解码器之间的注意力机制
        :param target_mask: 目标语言的掩码，用于解码器内部的自注意力机制
        """
        # 第一个子层，自注意力机制子层
        x = self.sublayer[0](x, lambda x:self.self_attn(x,x,x,target_mask))
        #第二个子层，源注意力机制子层(encoder_output要传2次)
        x = self.sublayer[1](x, lambda x: self.src_attn(x, encoder_output, encoder_output, source_mask))
        #第三个子层，前馈全连接层
        x = self.sublayer[2](x, lambda x: self.feed_forward(x))
        return x



#todo:测试解码器
def test_Decoderlayer():
    #定义变量
    y = torch.LongTensor([
        [1, 2, 3, 4, 5],
        [7, 8, 9, 10,11]
    ])
    my_embded = nn.Embedding(1000, 512)
    embded_y = my_embded(y)
    print(embded_y.shape)
    #传入位置编码
    position_y = PositionalEncoding(512, 0.5)
    position_y = position_y(embded_y)
    print(position_y.shape)
    #实例化子层head,embeded_dim,seq_len,dropout
    mult_head = MultiHeadedAttention(head=8, embeded_dim=512, seq_len=y.size(1),dropout=0.5)
    self_attn = copy.deepcopy(mult_head)
    src_attn = copy.deepcopy(mult_head)

    feed_forward = FeedForward(d_model=512, d_ff=2048)
    #获取编码器输出对象
    encoder_output = test_Encoder()

    #定义掩码张量
    source_mask = torch.zeros(8,5,5)
    target_mask = torch.zeros(8,5,5)

    decoderlayer = Decoderlayer(d_model = 512, self_attn=self_attn, src_attn=src_attn, feed_forward=feed_forward)
    decoder_output = decoderlayer(position_y, encoder_output, source_mask, target_mask)

    print(f'decoder_output.shape: {decoder_output.shape}')
    print(f'decoderlayer: \n{decoderlayer}')



#todo:定义解码器
class Decoder(nn.Module):
    def __init__(self,layer,N):
        """
        :param layer: 单个解码器层（Decoderlayer）
        :param N:解码器层的个数
        """
        super().__init__()
        self.layers = clones(layer, N)
        self.norm = LayerNorm(layer.d_model)

    def forward(self,x, encoder_output, source_mask, target_mask):
        for layer in self.layers:
            x = layer(x, encoder_output, source_mask, target_mask)
        return self.norm(x)



#todo:测试解码器
def test_Decoder():
    y = torch.LongTensor([
        [1, 2, 3, 4, 5],
        [7, 8, 9, 10, 11]
    ])
    my_embded = nn.Embedding(1000, 512)
    embded_y = my_embded(y)
    print(embded_y.shape)
    # 传入位置编码
    position_y = PositionalEncoding(512, 0.5)
    position_y = position_y(embded_y)
    print(position_y.shape)
    # 实例化子层head,embeded_dim,seq_len,dropout
    mult_head = MultiHeadedAttention(head=8, embeded_dim=512, seq_len=y.size(1), dropout=0.5)
    self_attn = copy.deepcopy(mult_head)
    src_attn = copy.deepcopy(mult_head)

    feed_forward = FeedForward(d_model=512, d_ff=2048)
    # 获取编码器输出对象
    encoder_output = test_Encoder()

    # 定义掩码张量
    source_mask = torch.zeros(8, 5, 5)
    target_mask = torch.zeros(8, 5, 5)

    decoderlayer = Decoderlayer(d_model=512, self_attn=self_attn, src_attn=src_attn, feed_forward=feed_forward)

    decoder = Decoder(decoderlayer, 6)
    result = decoder(position_y, encoder_output, source_mask, target_mask)
    print(f'result.shape: {result.shape}')
    print(f'decoder: \n{decoder}')
    return result

#todo；演示输出部分
class Generator(nn.Module):
    def __init__(self, d_model, vocab):
        super().__init__()
        self.linear = nn.Linear(d_model, vocab)

    def forward(self, x):
        x = self.linear(x)
        return F.log_softmax(x, dim=-1)


#todo:测试输出
def test_Generator():
    gen = Generator(512, 1000)
    y = test_Decoder()
    print(f'y.shape: {y.shape}')
    result= gen(y)
    print(f'result.shape: {result.shape}')
    return result


if __name__ == '__main__':
    # test_Decoderlayer()
    # test_Decoder()
    test_Generator()