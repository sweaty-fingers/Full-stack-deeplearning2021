import math
import torch
import torch.nn as nn
from torch import Tensor

class PositionalEncoding(torch.nn.Module):
    """
    encoder로 부터 생성된 feature-map에 추가하는 2-D positional encoding
    
    Following https://arxiv.org/abs/2103.06450 by Sumeet Singh.
    """
    
    def __init__(self, d_model: int, max_h: int = 2000, max_w: int = 2000) -> None:
        super().__init__()
        self.d_model = d_model
        assert d_model % 2 == 0, f"Embedding depth {d_model} is not even"
        pe = self.make_pe(d_model=d_model, max_h=max_h, max_w=max_w)  # (d_model, max_h, max_w)
        self.register_buffer("pe", pe)
        
    @staticmethod
    def make_pe(d_model: int, max_h: int, max_w: int) -> torch.Tensor:
        """
        포지셔널 인코딩을 생성한다.
        문단은 행과 열이 있으므로, d_model의 절반은 행을, 나머지 절반은 열의 인코딩을 사용하여 만든다.
        """
        
        pe_h = PositionalEncoding.make_pe(d_model=d_model // 2, max_len=max_h)  # (max_h, 1 d_model // 2)
        pe_h = pe_h.permute(2, 0, 1).expand(-1, -1, max_w)  # (d_model // 2, max_h, max_w)
        
        pe_w = PositionalEncoding.make_pe(d_model=d_model // 2, max_len=max_w)  # (max_w, 1, d_model // 2)
        pe_w = pe_w.permute(2, 1, 0).expand(-1, max_h, -1)  # (d_model // 2, max_h, max_w)
        
        pe = torch.cat([pe_h, pe_w], dim=0)  # (d_model, max_h, max_w)
        return pe
    
    def forward(self, x: Tensor) -> Tensor:
        """pytorch.nn.module.forward"""
        # x.shape = (B, d_model, H, W)
        assert x.shape[1] == self.pe.shape[0]
        x = x + self.pe[:, : x.size(2), : x.size(3)]  # type: ignore
        return x
    
        
class PositionalEncoding(torch.nn.Module):
    """
    Classic Attention-is-all-you-need positional encoding
    """

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000) -> None:
        super().__init__()
        self.dropout = torch.nn.Dropout(p=dropout)
        pe = self.make_pe(d_model=d_model, max_len=max_len)  # positional encoding??
        self.register_buffer("pe", pe) # 업데이트 하지 않는 layer 지정

    @staticmethod
    def make_pe(d_model: int, max_len: int) -> torch.Tensor:
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(
            1
        )  # (max_len,) -> (max_len, 1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)  # (max_len, d_model // 2)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(1)  # (max_len, 1, d_model)
        return pe

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x.shape = (S, B, d_model)
        assert x.shape[2] == self.pe.shape[2]
        x = x + self.pe[: x.size(0)]
        return self.dropout(x)



def generate_square_subsequent_mask(size: int) -> torch.Tensor:
    """
    Generate a triangular (size, size) mask.
    """

    mask = (torch.triu(torch.ones(size, size)) == 1).transpose(0, 1)
    mask = mask.float().masked_fill(mask == 0, float("-inf")).masked_fill(mask == 1, float(0.0))
    return mask
