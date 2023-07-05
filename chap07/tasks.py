from pyqs import task


@task(queue='math')
def add(x, y):
    print(f'{x} + {y} = {x + y}')
