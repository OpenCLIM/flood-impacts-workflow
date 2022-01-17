import json
from jinja2 import Template


def parameter_sets(workflow_version):
    with open('parameter_set.json') as f:
        template = Template(f.read())

    sets = []
    for return_period in [5, 10, 100]:
        for time_horizon in ['baseline', 2050, 2070]:
            s = template.render(time_horizon=time_horizon, return_period=return_period,
                                set_name=f'{return_period}yr {time_horizon}', workflow_version=workflow_version)

            sets.append(json.loads(s))
    return sets
