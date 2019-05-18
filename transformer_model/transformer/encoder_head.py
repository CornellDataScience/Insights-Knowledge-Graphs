import torch.nn as nn

class EncoderAverageHead(nn.Module):
    """
    Core encoder is a stack of N layers
    """

    def __init__(self):
        super(EncoderAverageHead, self).__init__()

    def forward(self, x):
        """
        Pass the input (and mask) through each layer in turn.
        """
        n_sents, n_tokens, n_dims = x.shape
        sent_means = torch.mean(x, 1)
        return sent_means.repeat(n_tokens,1,1).reshape(n_sents, n_tokens, n_dims)