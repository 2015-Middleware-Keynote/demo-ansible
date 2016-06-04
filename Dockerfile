FROM fedora:23
MAINTAINER RyanJ <ryanj@redhat.com>

ENV DEMO_ANSIBLE_VERSION=demo-ansible-2.1.2 \
    OPENSHIFT_ANSIBLE_VERSION=openshift-ansible-3.0.47-6 \
#    ANSIBLE_RPM_URL=https://dl.fedoraproject.org/pub/epel/7/x86_64/a/ansible1.9-1.9.6-2.el7.noarch.rpm \
    ANSIBLE_RPM_URL=https://kojipkgs.fedoraproject.org/packages/ansible/1.9.4/1.el7/noarch/ansible-1.9.4-1.el7.noarch.rpm \
    ANSIBLE_RPM_NAME=ansible \
    HOME=/opt/src

VOLUME /opt/src/keys

RUN set -ex && \
  dnf update -y && \
  INSTALL_PKGS="git bzip2 python python-boto python-click pyOpenSSL" && \
  dnf install -y --setopt=tsflags=nodocs $INSTALL_PKGS $ANSIBLE_RPM_URL && \
  rpm -V $INSTALL_PKGS $ANSIBLE_RPM_NAME && \
  git clone https://github.com/2015-Middleware-Keynote/demo-ansible -b $DEMO_ANSIBLE_VERSION ${HOME}/demo-ansible && \
  git clone https://github.com/openshift/openshift-ansible.git -b $OPENSHIFT_ANSIBLE_VERSION ${HOME}/openshift-ansible && \
  dnf clean all -y && \
  rm -rf /usr/share/man /tmp/*

WORKDIR ${HOME}/demo-ansible

ENTRYPOINT [ "./run.py" ]
