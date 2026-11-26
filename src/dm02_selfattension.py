import dm01_input
from dm01_input import *
import copy


def clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for _ in range(N)])

class MultiHeadedAttention(nn.Module):
    def __init__(self,head,embeded_dim,seq_len,dropout):
        super().__init__()
        self.head = head          #定义头数
        self.embeded_dim = embeded_dim
        self.dropout = nn.Dropout(p=dropout)
        # 词向量维度一定要整除头数，否则报错
        assert embeded_dim % head==0
        # 每个头分析的词向量维度
        self.d_k = embeded_dim // head
        self.seq_len = seq_len
        self.Linears = clones(nn.Linear(embeded_dim, embeded_dim), 4)
        self.attn = None        #占位符，方便后面传值

    def forward(self,query,key,value,mask=None):
        batch_size = query.size(0)
        query, key, value = [
            model(x).view(batch_size, self.seq_len, self.head, self.d_k).transpose(1, 2)
            for model, x in zip(self.Linears, (query, key, value))
        ]

        # epoch=0,model=self.Linear[0],x = query
        # epoch=1,model=self.Linear[1],x = key
        # epoch=2,model=self.Linear[2],x = value

       #进行Attention计算
        x, self.attn = attention(query, key, value, mask=mask, dropout=self.dropout)
        print(f'x.shape:{x.shape}')
        print(f'self.attn.shape:{self.attn.shape}')
       #x的shape是[batch_size,head,seq_len,d_k]
        x = x.transpose(1, 2).contiguous().view(batch_size, self.seq_len, self.head*self.d_k)
        #带入最后一个线性层计算
        return self.Linears[-1](x)

#todo:测试MultiHeadedAttention
def use_attesion():
    position_x = test_PositionalEncoding()
    print(f'position_x.shape:{position_x.shape}')
    query = key = value = position_x
    print(f'query.shape:{query.shape}')
    print(f'key.shape:{key.shape}')
    print(f'value.shape:{value.shape}')
    seq_len = query.size(1)
    #mask的shape是[head,seq_len,seq_len]
    mask = torch.zeros(8,5,5)
    my_attension = MultiHeadedAttention(head=8, embeded_dim=512, dropout=0.1,seq_len=seq_len)
    result = my_attension(query, key, value, mask)
    return result








#todo:初始化前馈全连接层
class FeedForward(nn.Module):
    # d_model是词向量的维度，d_ff是前馈全连接层指定的维度
    def __init__(self,d_model,d_ff,dropout_p = 0.5):
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.Linear1 = nn.Linear(d_model, d_ff)
        self.Linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(p=dropout_p)

    def forward(self,x):
        x =  self.Linear2(torch.relu(self.Linear1(x)))
        return x






#todo : 测试全连接层
def use_feedforward():
    #先拿到注意力机制的结果
    attn_x = use_attesion()
    my_feedfoward = FeedForward(d_model=512, d_ff=1024,dropout_p=0.5)
    result = my_feedfoward(attn_x)
    print(f'result.shape:{result.shape}')
    return result








if __name__ == '__main__':
    use_feedforward()

