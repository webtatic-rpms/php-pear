%if 0%{?scl:1}
%scl_package php-pear
%global _name %{name}
%global php_name %{?scl_prefix}php
%else
%global _name php-pear
%global php_name %{?php_name}%{!?php_name:php}
%global _root_bindir %{_bindir}
%global _root_sysconfdir %{_sysconfdir}
%endif

%global peardir %{_datadir}/pear
%global metadir %{_localstatedir}/lib/pear

%global getoptver 1.4.1
%global arctarver 1.4.2
%global structver 1.1.1
%global xmlutil   1.4.2

# Tests are only run with rpmbuild --with tests
# Can't be run in mock / koji because PEAR is the first package
%global with_tests       %{?_with_tests:1}%{!?_with_tests:0}

Summary: PHP Extension and Application Repository framework
Name: %{php_name}-pear
Version: 1.10.4
Release: 1%{?dist}
Epoch: 1
# PEAR, Archive_Tar, XML_Util are BSD
# Console_Getopt is PHP
# Structures_Graph is LGPLv2+
License: BSD and PHP and LGPLv2+
Group: Development/Languages
URL: http://pear.php.net/package/PEAR
Source0: http://download.pear.php.net/package/PEAR-%{version}.tgz
# wget https://raw.github.com/pear/pear-core/master/install-pear.php
Source1: install-pear.php
Source3: strip.php
Source10: pear.sh
Source11: pecl.sh
Source12: peardev.sh
Source13: macros.pear
Source21: http://pear.php.net/get/Archive_Tar-%{arctarver}.tgz
Source22: http://pear.php.net/get/Console_Getopt-%{getoptver}.tgz
Source23: http://pear.php.net/get/Structures_Graph-%{structver}.tgz
Source24: http://pear.php.net/get/XML_Util-%{xmlutil}.tgz
# Man pages
# https://github.com/pear/pear-core/pull/14
Source30: pear.1
Source31: pecl.1
Source32: peardev.1
# https://github.com/pear/pear-core/pull/16
Source33: pear.conf.5

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{php_name}-cli >= 5.1.0-1, %{php_name}-xml, gnupg
%if %{with_tests}
BuildRequires:  %{?scl_prefix}php-pear(pear.phpunit.de/PHPUnit)
%endif
%{?scl:Requires: %scl_runtime}

Requires:  %{php_name}-cli
# phpci detected extension
# PEAR (date, spl always builtin):
Requires:  %{php_name}-ftp
Requires:  %{php_name}-pcre
Requires:  %{php_name}-posix
Requires:  %{php_name}-tokenizer
Requires:  %{php_name}-xml
Requires:  %{php_name}-zlib
# Console_Getopt: pcre
# Archive_Tar: pcre, posix, zlib
Requires:  %{php_name}-bz2
# Structures_Graph: none
# XML_Util: pcre
# optional: overload and xdebug

Provides: %{name}(Console_Getopt) = %{getoptver}
Provides: %{name}(Archive_Tar) = %{arctarver}
Provides: %{name}(PEAR) = %{version}
Provides: %{name}(Structures_Graph) = %{structver}
Provides: %{name}(XML_Util) = %{xmlutil}
Provides: %{name}-XML-Util = %{xmlutil}
%if 0%{!?scl:1}
# Additional Provides for the original package name
Provides: php-pear = %{version}-%{release}
Provides: php-pear(Console_Getopt) = %{getoptver}
Provides: php-pear(Archive_Tar) = %{arctarver}
Provides: php-pear(PEAR) = %{version}
Provides: php-pear(Structures_Graph) = %{structver}
Provides: php-pear(XML_Util) = %{xmlutil}
Provides: php-pear-XML-Util = %{xmlutil}
%endif

%description
PEAR is a framework and distribution system for reusable PHP
components.  This package contains the basic PEAR components.

%prep
%setup -cT

# Create a usable PEAR directory (used by install-pear.php)
for archive in %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24}
do
    tar xzf  $archive --strip-components 1 || tar xzf  $archive --strip-path 1
    file=${archive##*/}
    [ -f LICENSE ] && mv LICENSE LICENSE-${file%%-*}
    [ -f README ]  && mv README  README-${file%%-*}

    tar xzf $archive 'package*xml'
    [ -f package2.xml ] && mv package2.xml ${file%%-*}.xml \
                        || mv package.xml  ${file%%-*}.xml
done
cp %{SOURCE1} %{SOURCE30} %{SOURCE31} %{SOURCE32} %{SOURCE33} .

# apply patches on used PEAR during install


%build
# This is an empty build section.


%install
rm -rf $RPM_BUILD_ROOT

export PHP_PEAR_SYSCONF_DIR=%{_sysconfdir}
export PHP_PEAR_SIG_KEYDIR=%{_sysconfdir}/pearkeys
export PHP_PEAR_SIG_BIN=%{_root_bindir}/gpg
export PHP_PEAR_INSTALL_DIR=%{peardir}

# 1.4.11 tries to write to the cache directory during installation
# so it's not possible to set a sane default via the environment.
# The ${PWD} bit will be stripped via relocate.php later.
export PHP_PEAR_CACHE_DIR=${PWD}%{_localstatedir}/cache/php-pear
export PHP_PEAR_TEMP_DIR=/var/tmp

install -d $RPM_BUILD_ROOT%{peardir} \
           $RPM_BUILD_ROOT%{_localstatedir}/cache/php-pear \
           $RPM_BUILD_ROOT%{_localstatedir}/www/html \
           $RPM_BUILD_ROOT%{_localstatedir}/lib/pear/pkgxml \
           $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm \
           $RPM_BUILD_ROOT%{_sysconfdir}/pear

export INSTALL_ROOT=$RPM_BUILD_ROOT

%{_bindir}/php -dmemory_limit=64M -dshort_open_tag=0 -dsafe_mode=0 \
         -d 'error_reporting=E_ALL&~E_DEPRECATED' -ddetect_unicode=0 \
         install-pear.php --force \
                 --dir      %{peardir} \
                 --cache    %{_localstatedir}/cache/php-pear \
                 --config   %{_sysconfdir}/pear \
                 --bin      %{_bindir} \
                 --www      %{_localstatedir}/www/html \
                 --doc      %{_docdir}/pear \
                 --test     %{_datadir}/tests/pear \
                 --data     %{_datadir}/pear-data \
                 --metadata %{metadir} \
                 %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24}

# Replace /usr/bin/* with simple scripts:
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT%{_bindir}/pear
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_bindir}/pecl
install -m 755 %{SOURCE12} $RPM_BUILD_ROOT%{_bindir}/peardev
for exe in pear pecl peardev; do
    sed -e 's:/usr:%{_prefix}:' \
        -i $RPM_BUILD_ROOT%{_bindir}/$exe
done

# Sanitize the pear.conf
%{_bindir}/php %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf ext_dir >new-pear.conf
%{_bindir}/php %{SOURCE3} new-pear.conf http_proxy > $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf

%{_bindir}/php -r "print_r(unserialize(substr(file_get_contents('$RPM_BUILD_ROOT%{_sysconfdir}/pear.conf'),17)));"


install -m 644 -c %{SOURCE13} \
           $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm/macros.%{_name}

# apply patches on installed PEAR tree
pushd $RPM_BUILD_ROOT%{peardir} 
 pushd PEAR
 popd
popd

# Why this file here ?
rm -rf $RPM_BUILD_ROOT/.depdb* $RPM_BUILD_ROOT/.lock $RPM_BUILD_ROOT/.channels $RPM_BUILD_ROOT/.filemap

# Need for re-registrying XML_Util
install -m 644 *.xml $RPM_BUILD_ROOT%{_localstatedir}/lib/pear/pkgxml

# The man pages
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install -p -m 644 pear.1 pecl.1 peardev.1 $RPM_BUILD_ROOT%{_mandir}/man1/
install -d $RPM_BUILD_ROOT%{_mandir}/man5
install -p -m 644 pear.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/

# make the cli commands available in standard root for SCL build
%if 0%{?scl:1}
install -m 755 -d $RPM_BUILD_ROOT%{_root_bindir}
ln -s %{_bindir}/pear      $RPM_BUILD_ROOT%{_root_bindir}/%{scl_prefix}pear
ln -s %{_bindir}/pecl      $RPM_BUILD_ROOT%{_root_bindir}/%{scl_prefix}pecl
%endif


%check
# Check that no bogus paths are left in the configuration, or in
# the generated registry files.
grep $RPM_BUILD_ROOT $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep %{_libdir} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep '"/tmp"' $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep /usr/local $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep -rl $RPM_BUILD_ROOT $RPM_BUILD_ROOT && exit 1


%if %{with_tests}
cd $RPM_BUILD_ROOT%{pear_phpdir}/test/Structures_Graph/tests
phpunit \
   -d date.timezone=UTC \
   -d include_path=.:$RPM_BUILD_ROOT%{pear_phpdir}:%{pear_phpdir}: \
   AllTests || exit 1

cd $RPM_BUILD_ROOT%{pear_phpdir}/test/XML_Util/tests
phpunit \
   -d date.timezone=UTC \
   -d include_path=.:$RPM_BUILD_ROOT%{pear_phpdir}:%{pear_phpdir}: \
   AllTests || exit 1
%else
echo 'Test suite disabled (missing "--with tests" option)'
%endif


%clean
rm -rf $RPM_BUILD_ROOT
rm new-pear.conf


%pre
# Manage relocation of metadata, before update to pear
if [ -d %{peardir}/.registry -a ! -d %{metadir}/.registry ]; then
  mkdir -p %{metadir}
  mv -f %{peardir}/.??* %{metadir}
fi


%post
# force new value as pear.conf is (noreplace)
current=$(%{_bindir}/pear config-get test_dir system)
if [ "$current" != "%{_datadir}/tests/pear" ]; then
%{_bindir}/pear config-set \
    test_dir %{_datadir}/tests/pear \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get data_dir system)
if [ "$current" != "%{_datadir}/pear-data" ]; then
%{_bindir}/pear config-set \
    data_dir %{_datadir}/pear-data \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get metadata_dir system)
if [ "$current" != "%{metadir}" ]; then
%{_bindir}/pear config-set \
    metadata_dir %{metadir} \
    system >/dev/null || :
fi


%triggerpostun -- %{?scl_prefix}php-pear-XML-Util
# re-register extension unregistered during postun of obsoleted %{?scl_prefix}php-pear-XML-Util
%{_bindir}/pear install --nodeps --soft --force --register-only \
    %{_localstatedir}/lib/pear/pkgxml/XML_Util.xml >/dev/null || :


%files
%defattr(-,root,root,-)
%{peardir}
%dir %{metadir}
%{metadir}/.channels
%verify(not mtime size md5) %{metadir}/.depdb
%verify(not mtime)%{metadir}/.depdblock
%verify(not mtime size md5)%{metadir}/.filemap
%verify(not mtime)%{metadir}/.lock
%{metadir}/.registry
%{metadir}/pkgxml
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/pear.conf
%{_root_sysconfdir}/rpm/macros.%{_name}
%dir %{_localstatedir}/cache/php-pear
%dir %{_localstatedir}/www/html
%dir %{_sysconfdir}/pear
%doc README* LICENSE*
%dir %{_docdir}/pear
%doc %{_docdir}/pear/*
%dir %{_datadir}/tests
%{_datadir}/tests/pear
%{_datadir}/pear-data
%{_mandir}/man1/pear.1*
%{_mandir}/man1/pecl.1*
%{_mandir}/man1/peardev.1*
%{_mandir}/man5/pear.conf.5*
%{?scl: %{_root_bindir}/%{scl_prefix}pear}
%{?scl: %{_root_bindir}/%{scl_prefix}pecl}


%changelog
* Sat Jun 10 2017 Andy Thompson <andy@webtatic.com> 1:1.10.4-1
- Update PEAR to 1.10.4
- Update dependencies to latest versions
- Support php_name insertion for reuse

* Sun Nov 08 2015 Andy Thompson <andy@webtatic.com> 1:1.10.1-1
- Update to PEAR-1.10.1
- Update dependencies to latest version
- Remove metadata and restcache patches applied upstream

* Sun Jun 14 2015 Andy Thompson <andy@webtatic.com> 1:1.9.5-1
- Update to PEAR-1.9.5
- Update dependencies to latest versions
- Update install-pear.php to latest version
- Remove PHP 4 compatibility from install-pear.php

* Wed Jul 09 2014 Andy Thompson <andy@webtatic.com> 1:1.9.4-2
- Fix PHP build dependency

* Tue Feb 04 2014 Andy Thompson <andy@webtatic.com> 1:1.9.4-1
- Fork php-pear
- Override non-SCL packages to php56w
