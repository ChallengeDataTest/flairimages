FROM continuumio/anaconda3:latest

# Copy environment.yml (if found) to a temp location so we update the conda environment.
COPY ./environment.yml  /tmp/conda-tmp/

RUN umask 0002 && \
    /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml && \
    rm -rf /tmp/conda-tmp

# p.i., does not actually expose the port
EXPOSE 8888:8888

CMD ["jupyter", "lab",\ 
     "--notebook-dir=/workspaces/flairimages",\  
     "--ip='*'",\ 
     "--port=8888", \ 
     "--no-browser", "--allow-root"]
