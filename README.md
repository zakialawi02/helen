# clifter_slam
clifter slam is a fully differentiable dense SLAM framework. It provides a repository of differentiable building blocks for a dense SLAM system, such as differentiable nonlienar least squares solvers, differentiable ICP (iterative closest point) techniques, differentiable raycastring modules, and differentiable mapping / fusion blocks. One can use these blocks to construct SLAM systems that allow gradients to flow all the way from the outputs of the system (map, trajectory) to the inputs (raw color / depth images, parameters, calibration)

## documentation
- [documentation](documentation/install.md)
- [online documentation](https://slowy07.github.io/clifter_slam)


## differentiable visual odometry
the beginnings of differentiable visual odometry can be traced back to seminal Lucas-Kanade iterative matching algorithm. apply the Lucas-Kanade algorithm to perform real-time dense visual odometry. Their system is differentiable, and has been extensively used for self-superviesd depth and motion estimation. coupled with the success of spatial transformer networks (STN), they can be used to perform dense visual odometry.

hoewever, extending differentiability beyodn the two view case (_frame-frame alingment_) is not starightforward. global consistency necessitates fusing measuerements from live frames into a global model (_model-frame alignment_) which is not trivially differentiable