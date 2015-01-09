#
# spec file for package crmsh
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%global gname haclient
%global uname hacluster
%global crmsh_docdir %{_defaultdocdir}/%{name}

%global upstream_version tip
%global upstream_prefix crmsh
%global crmsh_release 1

%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?rhel} || 0%{?fedora}
%define pkg_group System Environment/Daemons
%else
%define pkg_group Productivity/Clustering/HA
%endif

%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           crmsh
Summary:        High Availability cluster command-line interface
License:        GPL-2.0+
Group:          %{pkg_group}
Version:        2.2.0~rc2
Release:        %{?crmsh_release}%{?dist}
Url:            http://crmsh.github.io
Source0:        crmsh.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Requires(pre):  pacemaker
Requires:       python >= 2.6
Requires:       python-dateutil
Requires:       python-lxml
Requires:       python-parallax
Requires:       which
BuildRequires:  python-lxml
BuildRequires:  python-setuptools

%if 0%{?suse_version}
Requires:       python-PyYAML
# Suse splits this off into a separate package
Requires:       python-curses
BuildRequires:  fdupes
BuildRequires:  python-curses
%endif

%if 0%{?fedora_version}
Requires:       PyYAML
%endif

# Required for core functionality
BuildRequires:  asciidoc
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  pkgconfig
BuildRequires:  python

%if 0%{?suse_version} > 1210
# xsltproc is necessary for manpage generation; this is split out into
# libxslt-tools as of openSUSE 12.2.  Possibly strictly should be
# required by asciidoc
BuildRequires:  libxslt-tools
%endif

%if 0%{?suse_version} > 1110
BuildArch:      noarch
%endif

%description
The crm shell is a command-line interface for High-Availability
cluster management on GNU/Linux systems. It simplifies the
configuration, management and troubleshooting of Pacemaker-based
clusters, by providing a powerful and intuitive set of features.

Authors: Dejan Muhamedagic <dejan@suse.de> and many others

%package test
Summary:        Test package for crmsh
Group:          %{pkg_group}
Requires:       crmsh
%if 0%{?with_regression_tests}
BuildRequires:  corosync
BuildRequires:  procps
BuildRequires:  python-dateutil
BuildRequires:  python-nose
BuildRequires:  vim
Requires:       pacemaker

%if 0%{?suse_version} > 1110
BuildArch:      noarch
%endif

%if 0%{?suse_version}
BuildRequires:  libglue-devel
BuildRequires:  libpacemaker-devel
%else
BuildRequires:  cluster-glue-libs-devel
BuildRequires:  pacemaker-libs-devel
%endif

%endif
%description test
The crm shell is a command-line interface for High-Availability
cluster management on GNU/Linux systems. It simplifies the
configuration, management and troubleshooting of Pacemaker-based
clusters, by providing a powerful and intuitive set of features.

Authors: Dejan Muhamedagic <dejan@suse.de> and many others

%prep
%setup -q -n %{upstream_prefix}

# Force the local time
#
# 'hg archive' sets the file date to the date of the last commit.
# This can result in files having been created in the future
# when building on machines in timezones 'behind' the one the
# commit occurred in - which seriously confuses 'make'
find . -exec touch \{\} \;

%build
./autogen.sh

%{configure}            \
    --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_var}             \
    --with-pkg-name=%{name}     \
    --with-version=%{version}-%{release}    \
    --docdir=%{crmsh_docdir}

make %{_smp_mflags} docdir=%{crmsh_docdir}

%if 0%{?with_regression_tests}
	./test/unit-tests.sh --quiet
    if [ ! $? ]; then
        echo "Unit tests failed."
        exit 1
    fi
%endif

%install
make DESTDIR=%{buildroot} docdir=%{crmsh_docdir} install
install -Dm0644 contrib/bash_completion.sh %{buildroot}%{_sysconfdir}/bash_completion.d/crm.sh
%if 0%{?suse_version}
%fdupes %{buildroot}
%endif

%clean
rm -rf %{buildroot}

# Run regression tests after installing the package
# NB: this is called twice by OBS, that's why we touch the file
%if 0%{?with_regression_tests}
%post test
if [ ! -e /tmp/.crmsh_regression_tests_ran ]; then
    touch /tmp/.crmsh_regression_tests_ran
    if ! %{_datadir}/%{name}/tests/regression.sh ; then
        echo "Regression tests failed."
        cat crmtestout/regression.out
        exit 1
    fi
	cd %{_datadir}/%{name}/tests
	if ! ./cib-tests.sh ; then
		echo "CIB tests failed."
		exit 1
	fi
fi
%endif

%files
###########################################################
%defattr(-,root,root)

%{_sbindir}/crm
%{python_sitelib}/crmsh
%{python_sitelib}/crmsh*.egg-info

%{_datadir}/%{name}
%exclude %{_datadir}/%{name}/tests

%doc %{_mandir}/man8/*
%{crmsh_docdir}/COPYING
%{crmsh_docdir}/AUTHORS
%{crmsh_docdir}/crm.8.html
%{crmsh_docdir}/crmsh_hb_report.8.html
%{crmsh_docdir}/ChangeLog
%{crmsh_docdir}/README
%{crmsh_docdir}/contrib/*

%config %{_sysconfdir}/crm

%dir %{crmsh_docdir}
%dir %{crmsh_docdir}/contrib
%dir %attr (770, %{uname}, %{gname}) %{_var}/cache/crm
%config %{_sysconfdir}/bash_completion.d/crm.sh

%files test
%defattr(-,root,root)
%{_datadir}/%{name}/tests

%changelog
