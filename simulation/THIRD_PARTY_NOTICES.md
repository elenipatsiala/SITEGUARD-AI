# Third-party model attribution

The Go2 robot description and mesh assets come from Unitree Robotics' public `unitree_mujoco` repository, path `unitree_robots/go2`, pinned as a Git submodule at commit `1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d`.

Upstream: https://github.com/unitreerobotics/unitree_mujoco

The upstream BSD 3-Clause license is preserved in `assets/go2/LICENSE`. The source model remains unchanged in the submodule. `go2_front_camera.xml` is a project-side adaptation that adds a forward camera and adjusts the relative mesh directory for this scene.
