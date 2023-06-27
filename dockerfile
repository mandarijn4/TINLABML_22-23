FROM continuumio/miniconda3:23.3.1-0

LABEL maintainer="J.A.Boogaard@hr.nl"

# Set Timezone
RUN echo "Europe/Amsterdam" > /etc/timezone

RUN apt-get --yes update \
    && apt-get --yes upgrade

WORKDIR /opt/app

# Add requirements
RUN conda update --all \
    && conda install -y numpy==1.22.3 \
    && pip install --upgrade pip neurolab==0.3.5

# Add runtime code
ADD agent/*.py /opt/app/

EXPOSE 3001

ENTRYPOINT ["python", "/opt/app/agent.py"]