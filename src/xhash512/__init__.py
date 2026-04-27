#!/usr/bin/env python3

# Importando as funções/classes para o namespace principal do pacote
from .xhash512 import xh512
from .xbase64 import XBase64

__pname__ = "xhash512"
__author__ = "Fyllus (Geliardi D. Oliveira)"
__version__ = "0.2.0-alpha"

# Define o que será importado ao usar "from xhash512 import *"
__all__ = ["xh512", "XBase64"]