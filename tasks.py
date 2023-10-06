from invoke import task

DOCKER_TAG = "link_minimizer"


@task
def setup(ctx):
    ctx.run("pre-commit install")


@task
def build_images(ctx):
    ctx.run(f"docker build -t {DOCKER_TAG} .")


@task(pre=[build_images])
def local_dev(ctx):
    ctx.run(
        "docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up -d --remove-orphans"
    )
