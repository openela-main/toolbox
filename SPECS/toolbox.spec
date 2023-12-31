%global __brp_check_rpaths %{nil}

# RHEL's RPM toolchain doesn't like the compressed DWARF data generated by the
# Go toolchain.
%global _dwz_low_mem_die_limit 0
%global _find_debuginfo_dwz_opts %{nil}

Name:          toolbox
Version:       0.0.99.3

%global goipath github.com/containers/%{name}
%gometa

Release:       10%{?dist}
Summary:       Tool for containerized command line environments on Linux

License:       ASL 2.0
URL:           https://containertoolbx.org/

# https://github.com/containers/%%{name}/releases/download/%%{version}/%%{name}-%%{version}.tar.xz
# A vendored tarball was created from the upstream tarball:
# $ cd src
# $ go mod vendor
Source0:       %{name}-%{version}-vendored.tar.xz
Source1:       %{name}.conf

# https://bugzilla.redhat.com/show_bug.cgi?id=2033282
Patch0:        toolbox-Unbreak-sorting-and-clearly-identify-copied-images-in-list.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=2163752
Patch1:        toolbox-Support-RHEL-9-containers.patch

# RHEL specific
Patch100:      toolbox-Make-the-build-flags-match-RHEL-s-gobuild.patch
Patch101:      toolbox-Make-the-build-flags-match-RHEL-s-gobuild-for-PPC64.patch
Patch102:      toolbox-Add-migration-paths-for-coreos-toolbox-users.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1905383
ExcludeArch:   %{ix86}

BuildRequires: golang >= 1.19.13
BuildRequires: /usr/bin/go-md2man
BuildRequires: meson >= 0.58.0
BuildRequires: pkgconfig(bash-completion)
BuildRequires: systemd-rpm-macros

Requires:      containers-common
Requires:      podman >= 1.4.0


%description
Toolbox is a tool for Linux operating systems, which allows the use of
containerized command line environments. It is built on top of Podman and
other standard container technologies from OCI.


%package       tests
Summary:       Tests for %{name}

Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      coreutils
Requires:      gawk
Requires:      grep
Requires:      skopeo

%description   tests
The %{name}-tests package contains system tests for %{name}.


%prep
%setup -q

%patch0 -p1
%patch1 -p1

%ifnarch ppc64
%patch100 -p1
%else
%patch101 -p1
%endif

%patch102 -p1

# %%gomkdir is absent from RHEL 8.
GOBUILDDIR="$(pwd)/_build"
GOSOURCEDIR="$(pwd)"
if [[ ! -e "$GOBUILDDIR/bin" ]] ; then
  install -m 0755 -vd "$GOBUILDDIR/bin"
fi
if [[ ! -e "$GOBUILDDIR/src/%{goipath}" ]] ; then
  install -m 0755 -vd "$(dirname $GOBUILDDIR/src/%{goipath})"
  ln -fs "$GOSOURCEDIR" "$GOBUILDDIR/src/%{goipath}"
fi
cd "$GOBUILDDIR/src/%{goipath}"


%build
export GO111MODULE=off
GOBUILDDIR="$(pwd)/_build"
export GOPATH="$GOBUILDDIR:%{gopath}"
export CGO_CFLAGS="%{optflags} -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64"
ln -s src/cmd cmd
ln -s src/pkg pkg
ln -s src/vendor vendor

%meson \
    --buildtype=plain \
    -Dmigration_path_for_coreos_toolbox=true \
    -Dprofile_dir=%{_sysconfdir}/profile.d \
    -Dtmpfiles_dir=%{_tmpfilesdir}

%meson_build


%install
%meson_install
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/containers/%{name}.conf


%files
%doc CODE-OF-CONDUCT.md NEWS README.md SECURITY.md
%license COPYING
%{_bindir}/%{name}
%{_datadir}/bash-completion
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*
%config(noreplace) %{_sysconfdir}/containers/%{name}.conf
%{_sysconfdir}/profile.d/%{name}.sh
%{_tmpfilesdir}/%{name}.conf

%files tests
%{_datadir}/%{name}


%changelog
* Sat Oct 14 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-10
- Rebuild for CVE-2023-39325 and CVE-2023-44487
Resolves: RHEL-13122

* Mon Feb 06 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-9
- Rebuild for CVE-2022-41717
Resolves: #2164292

* Mon Jan 30 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-8
- Support RHEL 9 Toolbx containers
Resolves: #2163752

* Tue Dec 13 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-7
- Unbreak sorting and clearly identify copied images in 'list'
Resolves: #2033282

* Fri Oct 14 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-6
- Rebuild for CVE-2022-27664 and CVE-2022-32189
Resolves: #2116786

* Tue Aug 16 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-5
- Rebuild for CVE-2022-1705, CVE-2022-30630, CVE-2022-30631 and CVE-2022-30632
Resolves: #2111830

* Tue May 17 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-4
- Bump the minimum required golang version for added reassurance
Resolves: #2060769, #2089194

* Mon May 16 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-3
- Rebuild for FIPS-mode memory leak in the Go toolchain
Resolves: #2060769

* Wed May 11 2022 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-2
- BuildRequires: /usr/bin/go-md2man
- Related: #2061316

* Fri Dec 10 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-1
- Update to 0.0.99.3
- BuildRequire only systemd-rpm-macros as recommended by the Fedora packaging
  guidelines
- Update the Summary to match upstream
- Update the URL to point to the website
Resolves: #2000807

* Wed Sep 22 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-0.14.git660b6970e998
- Suggest a way forward if coreos/toolbox was used
Resolves: #2006802

* Wed Sep 22 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-0.13.git660b6970e998
- Switch to using the Toolbox-specific UBI image by default
Resolves: #2004563

* Thu Sep 16 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.12.git660b6970e998
- Changed image for tests and tests parameters to fix gating
  Related: #2000051

* Thu Sep 16 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.11.git660b6970e998
- Changed image for tests and added /etc/containers dir check
  Related: #2000051

* Tue Sep 14 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.10.git660b6970e998
- Added ability to force test system id and version id
  Related: #2000051

* Tue Sep 14 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.9.git660b6970e998
- Fixed test roles and changed default image path
  Related: #2000051

* Tue Sep 14 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.8.git660b6970e998
- Added default container image configuration for tests
  Related: #2000051

* Fri Sep 03 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.7.git660b6970e998
- Added missing gating tests files and patch for tests
  Related: #2000051

* Fri Sep 03 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.6.git660b6970e998
- re-add gating tests
- Related: #2000051

* Fri Sep 03 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.5.git660b6970e998
- Make sosreport work by setting the HOST environment variable
- Related: #2000051

* Mon Aug 30 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.4.git660b6970e998
- Fixed gating tests bats version
  Related: rhbz#1977343

* Tue Aug 24 2021 Oliver Gutiérrez <ogutierrez@redhat.com> - 0.0.99.3-0.3.git660b6970e998
- Rebuilt for gating checks
  Related: rhbz#1977343

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 0.0.99.3-0.2.git660b6970e998
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Mon Aug 02 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-0.1.git660b6970e998
- Fix the build on CentOS Stream
Related: #1970747

* Wed Jul 28 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2^1.git660b6970e998-1
- Add support for configuration files
- Related: #1970747

* Sat Jul 10 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-3
- Expose the host's entire / in the container at /run/host
- Resolves: #1977343

* Mon Jul 05 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-2
- Actually apply the patch to make 'toolbox' create or fall back to a
  container if possible
- Support logging into a registry if necessary
- Resolves: #1977343

* Fri Jul 02 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-1
- update to 0.99.2
- Resolves: #1977343

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 0.0.99.1-4
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Thu Apr 29 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.1-3
- Fix FTBFS
Resolves: #1912983

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.0.99.1-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Feb 23 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.1-1
- Update to 0.0.99.1

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.99-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Jan 12 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99-1
- Update to 0.0.99

* Mon Jan 11 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.98.1-2
- Harden the binary by using the same CGO_CFLAGS as on RHEL 8

* Thu Jan 07 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.98.1-1
- Update to 0.0.98.1

* Tue Jan 05 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.98-1
- Update to 0.0.98

* Wed Nov 25 2020 Ondřej Míchal <harrymichal@seznam.cz> - 0.0.97-2
- Move krb5-libs from -support to -experience, and update the list of packages
  in -experience

* Tue Nov 03 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.97-1
- Update to 0.0.97

* Thu Oct 01 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.96-1
- Update to 0.0.96

* Sun Aug 30 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.95-1
- Update to 0.0.95

* Mon Aug 24 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.94-1
- Update to 0.0.94

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.93-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat Jul 25 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.93-1
- Update to 0.0.93

* Fri Jul 03 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.92-1
- Update to 0.0.92

* Fri Jul 03 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.91-2
- Fix the 'toolbox --version' output

* Tue Jun 30 2020 Harry Míchal <harrymichal@seznam.cz> - 0.0.91-1
- Update to 0.0.91

* Sat Jun 27 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.18-5
- Remove ExclusiveArch to match Podman

* Wed Jun 10 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.18-4
- Sync the "experience" packages with the current Dockerfile
- Make "experience" Require "support"

* Fri Apr 03 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.18-3
- Drop compatibility Obsoletes and Provides for fedora-toolbox

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Jan 14 2020 Debarshi Ray <rishi@fedoraproject.org> - 0.0.18-1
- Update to 0.0.18

* Wed Nov 20 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.17-1
- Update to 0.0.17

* Tue Oct 29 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.16-1
- Update to 0.0.16

* Mon Sep 30 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.15-1
- Update to 0.0.15

* Wed Sep 18 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.14-1
- Update to 0.0.14

* Thu Sep 05 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.13-1
- Update to 0.0.13

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 22 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.12-1
- Update to 0.0.12

* Tue Jun 25 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.11-2
- Require flatpak-session-helper

* Fri Jun 21 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.11-1
- Update to 0.0.11

* Tue May 21 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.10-1
- Update to 0.0.10

* Tue Apr 30 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.9-1
- Update to 0.0.9

* Tue Apr 16 2019 Adam Williamson <awilliam@redhat.com> - 0.0.8-2
- Rebuild with Meson fix for #1699099

* Fri Apr 12 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.8-1
- Update to 0.0.8

* Thu Mar 14 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.7-1
- Update to 0.0.7

* Fri Feb 22 2019 Debarshi Ray <rishi@fedoraproject.org> - 0.0.6-1
- Initial build after rename from fedora-toolbox
