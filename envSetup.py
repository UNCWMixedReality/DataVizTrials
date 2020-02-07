import json

from tasks.models import Environments

## the following sets up the environment options in the db
envs = ['vr','desktop','tablet']
grids = [True, False]

for env in envs:
     for grid in grids:
        new_env = Environments()
        new_env.device = env
        new_env.grid = grid
        new_env.save()
 