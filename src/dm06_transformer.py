"""
演示Transformer
"""
import copy

from dm05_decoderlayer import *

class my_transformer(nn.Module):
    def __init__(self,source_embded,encoder,target_embded,decoder,generator):
        """
        :param source_embded: 输入部分的词嵌入层+位置编码
        :param encoder: 编码器
        :param target_embded:真实值输入部分的词嵌入层+位置编码
        :param decoder:解码器
        :param generator:输出部分
        """
        super().__init__()
        self.source_embded = source_embded
        self.encoder = encoder
        self.target_embded = target_embded
        self.decoder = decoder
        self.generator = generator

    def forward(self,source_x,target_y,source_mask,target_mask):
        """
        :param source_x: 输入部分,形状为[batch_size,seq_len,d_model]
        :param target_y: 真实值输入部分,形状为[batch_size,seq_len,d_model]
        :param source_mask: 输入部分的掩码,(padding mask),防止补丁部分的干扰，形状为[head,seq_len,seq_len]
        :param target_mask: 真实值输入部分的掩码,(sentence mask)，防止未来信息泄露，形状为[head,seq_len,seq_len]
        """
        emmbeded_x = self.source_embded(source_x)
        encoder_output = self.encoder(emmbeded_x,source_mask)
        emmbeded_y = self.target_embded(target_y)
        decoder_output = self.decoder(emmbeded_y,encoder_output,source_mask,target_mask)
        return self.generator(decoder_output)


#todo:测试Transformer
def test_Transformer():
    #实例化编码器
    #head,embeded_dim,seq_len,dropout
    mha = MultiHeadedAttention(8, 512,seq_len = 5 ,dropout = 0.5)
    ff = FeedForward(512, 1024)
    #d_model,self_attn,feed_forward,dropout=0.5
    layer1 = Encoderlayer(d_model = 512, self_attn = mha, feed_forward = ff, dropout = 0.5)
    encoder = Encoder(layer1, 6)
    #实例化解码器
    self_attn = copy.deepcopy(mha)
    src_attn = copy.deepcopy(mha)
    layer2 = Decoderlayer(d_model = 512, self_attn = self_attn, src_attn=src_attn, feed_forward = ff, dropout = 0.5)
    decoder = Decoder(layer2, 6)

    vocab_size = 1000
    d_model = 512
    dropout_p = 0.5
    my_embded = nn.Embedding(vocab_size, d_model)
    my_pe = PositionalEncoding(d_model, dropout_p)
    source_embded = nn.Sequential(my_embded, my_pe)
    target_embded = copy.deepcopy(source_embded)

    generator = Generator(d_model, vocab_size)

    transformer = my_transformer(source_embded, encoder, target_embded, decoder, generator)

    source_x = torch.LongTensor([
        [1, 2, 3, 4, 5],
        [7, 8, 9, 10, 11]
    ])
    target_y = torch.LongTensor([
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10]
    ])
    source_mask = torch.zeros(8,5,5)
    target_mask = torch.zeros(8,5,5)
    output = transformer(source_x, target_y, source_mask, target_mask)
    print(f"output.shape:{output.shape}")


if __name__ == '__main__':
    test_Transformer()
