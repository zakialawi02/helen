# clifter_slam
clifter slam is a fully differentiable dense SLAM framework. It provides a repository of differentiable building blocks for a dense SLAM system, such as differentiable nonlienar least squares solvers, differentiable ICP (iterative closest point) techniques, differentiable raycastring modules, and differentiable mapping / fusion blocks. One can use these blocks to construct SLAM systems that allow gradients to flow all the way from the outputs of the system (map, trajectory) to the inputs (raw color / depth images, parameters, calibration)


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
