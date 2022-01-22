import torch
import torch.nn as nn

from Components.PatchEncoder import PatchEncoder
from Components.Tranformer import Transformer
from Components.MLP import MLP


class Discriminator(nn.Module):
    def __init__(self, img_size, n_channels, output_size, n_transformer_layers=1, encoder_params=None, transformer_params=None, mlp_params=None, **kwargs):
        super(Discriminator, self).__init__()

        self.img_size             = img_size
        self.n_channels           = n_channels
        self.output_size          = output_size
        self.n_transformer_layers = n_transformer_layers

        self.encoder_params     = {} if encoder_params is None else encoder_params
        self.transformer_params = {} if transformer_params is None else transformer_params
        self.mlp_params         = {} if mlp_params is None else mlp_params

        self.encoder_params['img_size'], self.encoder_params['n_channels'] = self.img_size, self.n_channels
        self.patch_encoder = PatchEncoder(**self.encoder_params)

        self.transformer_params['in_features'] = self.patch_encoder.token_size
        self.transformer_layers = nn.ModuleList([Transformer(**self.transformer_params) for _ in range(self.n_transformer_layers)])

        self.mlp_params['in_features'], self.mlp_params['out_features'] = self.transformer_layers[-1].in_features, self.output_size
        self.mlp = MLP(**kwargs)

        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, imgs):
        tokens = self.patch_encoder(imgs)
        for transformer in self.transformer_layers:
            tokens = transformer(tokens)
        output = self.mlp(tokens[:, 0, :])  # we compute the output only with the cls token
        return self.sigmoid(output)
