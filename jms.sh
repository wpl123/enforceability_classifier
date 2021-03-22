#
#maps working directory to /opt/notebooks
#
#	https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html

WORKDIR=$PWD/data
#WORKDIR=$HOME/dockers/waterdata_frontend/data
docker run --user root --rm -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -e GRANT_SUDO=yes -v $WORKDIR:/home/jovyan/work jms

#jupyter/datascience-notebook:
#latest
#9b06df75e445



#
#	https://stackoverflow.com/questions/48842668/running-condas-jupyter-on-docker
#docker run -t --rm -p 8888:8888 -v /media/wplaird/development/data_science/notebooks:/opt/notebooks continuumio/anaconda2 /bin/bash -c "/opt/conda/bin/jupyter notebook --ip=0.0.0.0 --port=8888 --notebook-dir=/opt/notebooks --allow-root --no-browser"

#
#	https://medium.com/@patrickmichelberger/getting-started-with-anaconda-docker-b50a2c482139
#docker run -i -t -p 8888:8888 continuumio/anaconda3 /bin/bash -c “/opt/conda/bin/conda install jupyter -y — quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook — notebook-dir=/opt/notebooks — ip=’*’ — port=8888 — no-browser”
