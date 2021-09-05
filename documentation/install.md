# installation

## torch install
to install PyTorch via pip , and do have a [CUDA-Capable](https://developer.nvidia.com/cuda-zone) system, in the above selector, choose os : ``linux``, package: ``pip`` and the CUDA version suited to your machine. the latest CUDA version is better. Then run the command that is presented to you

## verification
to ensure that PyTorch was installed correctly, we can verify by running sample PyTorch code.

```python
import torch
a = torch.rand(5,3)
print(a)
```
