%global srcname dmx_trigger

Name:           python-%{srcname}
Version:        0.1.0
Release:        1%{?dist}
Summary:        An OLA DMX Video trigger package

License:        MIT
URL:            https://github.com/linuxnow/dmx_trigger
Source0:        %{pypi_source}

BuildArch:      noarch

%global _description %{expand:
A python module to monitor DMX traffic and trigger actions based on
the channel number.

There are  two classes:
-a DMX monitor
-a video provider

You provide callback functions to the video provider so tht they can be
triggered when DMX data arrives.}


%description %_description

%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%description -n python3-%{srcname} %_description

%prep
%autosetup -n %{srcname}-%{version}
rm -rf %{eggname}.egg-info

%build
%py3_build

%install
%py3_install

# Note that there is no %%files section for the unversioned python module
%files -n python3-%{srcname}
%{!?_licensedir:%global license %doc}
%doc README.md
%{python3_sitelib}/%{srcname}-*.egg-info/
%{python3_sitelib}/%{srcname}/
%{_bindir}/vlc_video_provider.py
