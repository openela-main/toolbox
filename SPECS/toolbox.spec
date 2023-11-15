%global __brp_check_rpaths %{nil}

Name:          toolbox
Version:       0.0.99.4

%global goipath github.com/containers/%{name}
%gometa

Release:       5%{?dist}
Summary:       Tool for containerized command line environments on Linux

License:       ASL 2.0
URL:           https://containertoolbx.org/

Source0:       https://github.com/containers/%{name}/releases/download/%{version}/%{name}-%{version}-vendored.tar.xz
Source1:       %{name}.conf

# Upstream
Patch0:        toolbox-Don-t-use-podman-1-when-generating-the-comp.patch
Patch1:        toolbox-Don-t-validate-subordinate-IDs-when-generat.patch
Patch2:        toolbox-cmd-initContainer-Be-aware-of-security-hardened-moun.patch

# RHEL specific
Patch100:      toolbox-Make-the-build-flags-match-RHEL-s-gobuild.patch
Patch101:      toolbox-Make-the-build-flags-match-RHEL-s-gobuild-for-PPC64.patch
Patch102:      toolbox-Add-migration-paths-for-coreos-toolbox-users.patch

BuildRequires: gcc
BuildRequires: golang >= 1.20.4
BuildRequires: /usr/bin/go-md2man
BuildRequires: meson >= 0.58.0
BuildRequires: pkgconfig(bash-completion)
BuildRequires: shadow-utils-subid-devel
BuildRequires: systemd
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
%patch2 -p1

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
    -Dfish_completions_dir=%{_datadir}/fish/vendor_completions.d \
    -Dmigration_path_for_coreos_toolbox=true \
    -Dprofile_dir=%{_sysconfdir}/profile.d \
    -Dtmpfiles_dir=%{_tmpfilesdir} \
    -Dzsh_completions_dir=%{_datadir}/zsh/site-functions

%meson_build


%install
%meson_install
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/containers/%{name}.conf


%files
%doc CODE-OF-CONDUCT.md NEWS README.md SECURITY.md
%license COPYING src/vendor/modules.txt
%{_bindir}/%{name}
%{_datadir}/bash-completion
%{_datadir}/fish
%{_datadir}/zsh
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*
%{_mandir}/man5/%{name}.conf.5*
%config(noreplace) %{_sysconfdir}/containers/%{name}.conf
%{_sysconfdir}/profile.d/%{name}.sh
%{_tmpfilesdir}/%{name}.conf

%files tests
%{_datadir}/%{name}


%changelog
* Fri Aug 11 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.4-5
- Be aware of security hardened mount points
Resolves: #2231464

* Mon Aug 07 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.4-4
- Rebuild for CVE-2023-24539, CVE-2023-24540 and CVE-2023-29400
Resolves: #2207509

* Mon Jul 10 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.4-3
- Rebuild for CVE-2022-41723, CVE-2023-24534, CVE-2023-24536 and
  CVE-2023-24538
Resolves: #2187343, #2187363, #2203694

* Mon Jul 10 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.4-2
- Rebuild for CVE-2022-41724 and CVE-2022-41725
Resolves: #2179947

* Tue Apr 04 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.4-1
- Update to 0.0.99.4
- Fix CVE-2022-3064
Resolves: #2164980, #2165743

* Mon Feb 06 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-7
- Rebuild for CVE-2022-41717
Resolves: #2163737

* Mon Jan 30 2023 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-6
- Support RHEL 9 Toolbx containers
Resolves: #2165610

* Tue Dec 13 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-5
- Unbreak sorting and clearly identify copied images in 'list'
Resolves: #2152907

* Mon Nov 07 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-4
- Rebuild for CVE-2022-27664 and CVE-2022-32189
Resolves: #2116761, #2126749

* Mon Nov 07 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-3
- Rebuild for CVE-2022-1705, CVE-2022-30630, CVE-2022-30631 and CVE-2022-30632
Resolves: #2111827

* Mon Nov 07 2022 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-2
- Update to 0.0.99.3
- BuildRequire only systemd-rpm-macros as recommended by the Fedora packaging
  guidelines
- Update the Summary to match upstream
- Update the URL to point to the website
Resolves: #2115089

* Fri Apr 08 2022 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.5
- bump golang BR to 1.17.7
- Related: #2061390

* Mon Sep 20 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.4
- Switch to using the Toolbox-specific UBI image by default
- Related: #2001445

* Thu Sep 02 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.99.3-0.3
- Suggest a way forward if coreos/toolbox was used
Resolves: #1998191, #2000914

* Thu Aug 26 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.2
- Make sosreport work by setting the HOST environment variable
- Related: #1934415

* Wed Aug 11 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-0.1
- change release to 0.x so it is obvious it is devel version
- Related: #1934415

* Thu Aug 05 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.3-1
- Fix the build on CentOS Stream
- Related: #1934415

* Wed Jul 28 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2^1.git660b6970e998-1
- Add support for configuration files
Resolves: #1940082
- Related: #1934415

* Mon Jul 26 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-4
- Instead of offering to log into a registry, just mention 'podman login'
- Related: #1934415

* Sat Jul 10 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-3
- Expose the host's entire / in the container at /run/host
- Related: #1934415

* Mon Jul 05 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-2
- Actually apply the patch to make 'toolbox' create or fall back to a
  container if possible
- Support logging into a registry if necessary
- Related: #1934415

* Fri Jul 02 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99.2-1
- Update to 0.0.99.2
- Make 'toolbox' create or fall back to a container if possible
Resolves: #1914687
- Related: #1934415

* Tue Jan 12 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.99-1
- Update to 0.0.99
- Related: #1883490

* Tue Jan 12 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.98.1-3
- remove bats as it's not present in RHEL
- Related: #1883490

* Mon Jan 11 2021 Jindrich Novy <jnovy@redhat.com> - 0.0.98.1-2
- harden the toolbox binary
- minor fixes
- Related: #1883490

* Fri Jan 08 2021 Debarshi Ray <rishi@fedoraproject.org> - 0.0.98.1-1
- Rebase to github.com/containers/toolbox
