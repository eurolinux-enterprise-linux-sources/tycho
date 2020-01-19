# Bootstrap build
# Set this if Tycho and Eclipse are not in buildroot
%global bootstrap 0
# When building version under development (non-release)
# %%global snap -SNAPSHOT
%global snap %{nil}

%define __requires_exclude osgi*

Name:           tycho
Version:        0.19.0
Release:        5%{?dist}
Summary:        Plugins and extensions for building Eclipse plugins and OSGI bundles with Maven

Group:          Development/Libraries
# license file is missing but all files having some licensing information are ASL 2.0
License:        ASL 2.0
URL:            http://tycho.sonatype.org/
Source0:        http://git.eclipse.org/c/tycho/org.eclipse.tycho.git/snapshot/tycho-0.19.x.tar.bz2

# this is a workaround for maven-plugin-plugin changes that happened after
# version 2.4.3 (impossible to have empty mojo created as aggregate). This
# should be fixed upstream properly
Source1:        EmptyMojo.java
# we need to make sure we are using maven 3 deps
Source2:        depmap.xml
Source3:        copy-platform-all
# Bootstrap repo for building when Tycho and Eclipse not built.
%if %{bootstrap}
Source4:        maven-repo.tar.xz
%endif

Patch0:         %{name}-fix-build.patch
# Upstream builds against maven-surefire 2.12.3
Patch1:         %{name}-maven-surefire.patch
Patch2:         %{name}-fix-surefire.patch
Patch3:         %{name}-use-custom-resolver.patch
# Set some temporary build version so that the bootstrapped build has
# a different version from the nonbootstrapped. Otherwise there will
# be cyclic dependencies.
Patch4:         %{name}-bootstrap.patch
# Additional changes needed just for bootstrap build
Patch7:         %{name}-fix-bootstrap-build.patch

BuildArch:      noarch

BuildRequires:  jpackage-utils
BuildRequires:  java-devel
BuildRequires:  maven-local
BuildRequires:  maven-clean-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-dependency-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-jar-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-release-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-shared-verifier
BuildRequires:  maven-shared-osgi
BuildRequires:  maven-surefire-plugin
BuildRequires:  maven-surefire-provider-junit
BuildRequires:  maven-surefire-provider-junit4
BuildRequires:  objectweb-asm4
BuildRequires:  plexus-containers-component-metadata
BuildRequires:  decentxml
BuildRequires:  easymock3
BuildRequires:  ecj
BuildRequires:  maven-plugin-testing-harness
%if ! %{bootstrap}
BuildRequires:  osgi(org.eclipse.jdt)
BuildRequires:  %{name}
%endif
BuildRequires:  maven-shared-utils
BuildRequires:  mockito

Requires:       jpackage-utils
Requires:       decentxml
Requires:       maven-local
Requires:       maven-clean-plugin
Requires:       maven-dependency-plugin
Requires:       maven-shared-verifier
Requires:       maven-surefire-provider-junit4
Requires:       objectweb-asm4
Requires:       ecj
%if ! %{bootstrap}
Requires:       osgi(org.eclipse.platform)
%endif

# Tycho always tries to resolve all build plugins, even if they are
# not needed during Maven lifecycle.  This means that Tycho will try
# to resolve plugins like clean, deploy or site, which aren't normally
# used during package build.  See rhbz#971301
Requires:       maven-clean-plugin
Requires:       maven-compiler-plugin
Requires:       maven-deploy-plugin
Requires:       maven-install-plugin
Requires:       maven-jar-plugin
Requires:       maven-resources-plugin
Requires:       maven-site-plugin
Requires:       maven-surefire-plugin


%description
Tycho is a set of Maven plugins and extensions for building Eclipse
plugins and OSGI bundles with Maven. Eclipse plugins and OSGI bundles
have their own metadata for expressing dependencies, source folder
locations, etc. that are normally found in a Maven POM. Tycho uses
native metadata for Eclipse plugins and OSGi bundles and uses the POM
to configure and drive the build. Tycho supports bundles, fragments,
features, update site projects and RCP applications. Tycho also knows
how to run JUnit test plugins using OSGi runtime and there is also
support for sharing build results using Maven artifact repositories.

Tycho plugins introduce new packaging types and the corresponding
lifecycle bindings that allow Maven to use OSGi and Eclipse metadata
during a Maven build. OSGi rules are used to resolve project
dependencies and package visibility restrictions are honored by the
OSGi-aware JDT-based compiler plugin. Tycho will use OSGi metadata and
OSGi rules to calculate project dependencies dynamically and injects
them into the Maven project model at build time. Tycho supports all
attributes supported by the Eclipse OSGi resolver (Require-Bundle,
Import-Package, Eclipse-GenericRequire, etc). Tycho will use proper
classpath access rules during compilation. Tycho supports all project
types supported by PDE and will use PDE/JDT project metadata where
possible. One important design goal in Tycho is to make sure there is
no duplication of metadata between POM and OSGi metadata.



%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{name}-0.19.x

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

find tycho-core -iname '*html' -delete

sed -i -e 's/org.apache.maven.it.util.DirectoryScanner/org.apache.maven.shared.utils.io.DirectoryScanner/g' tycho-testing-harness/src/main/java/org/eclipse/tycho/test/AbstractTychoIntegrationTest.java

# Move from org.sonatype.aether to org.eclipse.aether
find . -name "*.java" | xargs sed -i 's/org.sonatype.aether/org.eclipse.aether/g'
find . -name "*.java" | xargs sed -i 's/org.eclipse.aether.util.DefaultRepositorySystemSession/org.eclipse.aether.DefaultRepositorySystemSession/g'
sed -i 's/public int getPriority/public float getPriority/g' tycho-core/src/main/java/org/eclipse/tycho/core/p2/P2RepositoryConnectorFactory.java

# place empty mojo in place
mkdir -p tycho-maven-plugin/src/main/java/org/fedoraproject
pushd tycho-maven-plugin/src/main/java/org/fedoraproject
cp %{SOURCE1} .
popd

# Bootstrap Build
%if %{bootstrap}
tar -xf %{SOURCE4}

# EXACT version in reactor cache to build against when bootstrapping
# If we built our own Tycho locally and put it into reactor cache instead
# of using upstream's then we need to make sure the build finds it.
sed -i 's/<tychoBootstrapVersion>0.16.0<\/tychoBootstrapVersion>/<tychoBootstrapVersion>0.18.0<\/tychoBootstrapVersion>/' pom.xml

# gid:aid used by bootstrapped build dependencies
mkdir -p .m2/org/ow2/asm/asm-debug-all/4.0/
pushd .m2/org/ow2/asm/asm-debug-all/4.0/
ln -s %{_mavenpomdir}/JPP.objectweb-asm4-asm-all.pom asm-debug-all-4.0.pom
ln -s %{_javadir}/objectweb-asm4/asm-all.jar asm-debug-all-4.0.jar
popd

%patch7 -p1

# Tycho can't use cached composite repository metadata so use other type
sed -i 's/releases\/kepler\//releases\/kepler\/201306260900/' tycho-bundles/tycho-bundles-target/tycho-bundles-target.target

# Non-Bootstrap Build
%else

# Tests are skipped anyways, so remove some test dependencies
%pom_xpath_remove "pom:dependency[pom:classifier='tests']" tycho-compiler-plugin
%pom_xpath_remove "pom:dependency[pom:classifier='tests']" tycho-packaging-plugin

# These units cannot be found during a regular build
sed -i '/^<unit id=.*$/d' tycho-bundles/tycho-bundles-target/tycho-bundles-target.target

# installed version of Tycho
sysVer=`grep -C 1 "<artifactId>tycho</artifactId>" %{_mavenpomdir}/JPP.tycho-main.pom | grep "version" | sed 's/.*>\(.*\)<.*/\1/'`

# build version of Tycho
buildVer=`grep -C 1 "<artifactId>tycho</artifactId>" pom.xml | grep "version" | sed 's/.*>\(.*\)<.*/\1/'`

echo "System version is ${sysVer} and attempting to build ${buildVer}."

# If version installed on system is the same as the version being built
# an intermediary build must be done to prevent a cycle at build time.
if [ "${sysVer}" == "${buildVer}" ]; then
echo "Performing intermediary build"
%patch4 -p1

mvn-rpmbuild -Dmaven.local.depmap.file=%{SOURCE2} -DskipTychoVersionCheck -Dmaven.test.skip=true install javadoc:aggregate

%patch4 -p1 -R

# EXACT version in reactor cache to build against (%%{version}-SNAPSHOT)
sed -i 's/<tychoBootstrapVersion>0.18.1<\/tychoBootstrapVersion>/<tychoBootstrapVersion>0.19.0-SNAPSHOT<\/tychoBootstrapVersion>/' pom.xml
fi

%endif

%build
mvn-rpmbuild -Dmaven.local.depmap.file=%{SOURCE2} -DskipTychoVersionCheck -Dmaven.test.skip=true clean install javadoc:aggregate

%install

mkdir -p $RPM_BUILD_ROOT%{_javadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

# pom and jar installation
for mod in target-platform-configuration tycho-compiler-{jdt,plugin} \
           tycho-{artifactcomparator,core,embedder-api,metadata-model,testing-harness} \
           sisu-equinox/sisu-equinox{-api,-launching,-embedder} \
           tycho-p2/tycho-p2-{facade,plugin,{director,publisher,repository}-plugin} \
           tycho-{maven,packaging,pomgenerator,release/tycho-versions,source}-plugin \
           tycho-bundles/org*  \
           tycho-surefire/{tycho-surefire-plugin,org.eclipse.tycho.surefire.{osgibooter,junit,junit4{,7}}}; do
   echo $mod
   aid=`basename $mod`
   install -pm 644 $mod/pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$aid.pom
   install -m 644 $mod/target/$aid-%{version}%{snap}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/$aid.jar
   %add_maven_depmap JPP.%{name}-$aid.pom %{name}/$aid.jar -a "org.eclipse.tycho:$aid,org.sonatype.tycho:$aid"
done

# pom installation
for pommod in tycho-p2 tycho-bundles tycho-surefire \
              tycho-release sisu-equinox; do
   aid=`basename $pommod`
   install -pm 644 $pommod/pom.xml \
               $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-$aid.pom
   %add_maven_depmap JPP.%{name}-$aid.pom -a "org.eclipse.tycho:$aid,org.sonatype.tycho:$aid"
done

# p2 runtime
pushd tycho-bundles/tycho-bundles-external
install -pm 644 pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-tycho-bundles-external.pom
install -m 644 target/tycho-bundles-external-%{version}*.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external.zip
ln -s tycho-bundles-external.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-bundles-external.jar
%add_maven_depmap -f zip JPP.%{name}-tycho-bundles-external.pom %{name}/tycho-bundles-external.jar -a "org.eclipse.tycho:tycho-bundles-external,org.sonatype.tycho:tycho-bundles-external"
popd

# main
install -pm 644 pom.xml  $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-main.pom
%add_maven_depmap JPP.%{name}-main.pom -a "org.eclipse.tycho:$aid,org.sonatype.tycho:$aid"

# standalone p2 director
pushd .m2/org/eclipse/tycho/tycho-standalone-p2-director/%{version}*/
install -m 644 tycho-standalone-p2-director-%{version}*.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-standalone-p2-director.zip
ln -s tycho-standalone-p2-director.zip $RPM_BUILD_ROOT%{_javadir}/%{name}/tycho-standalone-p2-director.jar
install -pm 644 tycho-standalone-p2-director-%{version}*.pom $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-tycho-standalone-p2-director.pom
popd
%add_maven_depmap -f zip JPP.%{name}-tycho-standalone-p2-director.pom tycho/tycho-standalone-p2-director.jar -a "org.eclipse.tycho:tycho-standalone-p2-director,org.sonatype.tycho:tycho-standalone-p2-director"

# javadoc
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/api*/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

install -pm 755 %{SOURCE3} $RPM_BUILD_ROOT%{_javadir}/%{name}/copy-platform-all

%if %{bootstrap}
# org.eclipse.osgi
osgiJarPath=`find ".m2" -name "org.eclipse.osgi_*.jar"`
osgiJar=`basename $osgiJarPath`
osgiVer=`echo $osgiJar | sed 's/^.*_//' | sed 's/.jar//'`

mvn-rpmbuild org.apache.maven.plugins:maven-install-plugin:install-file \
-Dfile=$osgiJarPath \
-Dpackaging=jar \
-DgroupId=org.eclipse.tycho \
-DartifactId=org.eclipse.osgi \
-Dversion=$osgiVer

osgiPomPath=`find ".m2/org/eclipse/tycho/org.eclipse.osgi" -name "org.eclipse.osgi-$osgiVer.pom"`

install -pm 644 $osgiPomPath $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.tycho-osgi.pom
install -m 644 $osgiJarPath $RPM_BUILD_ROOT%{_javadir}/%{name}/osgi.jar
%add_maven_depmap JPP.%{name}-osgi.pom %{name}/osgi.jar -a "org.eclipse.tycho:org.eclipse.osgi"
%endif

# This is a temporary workaround for rhbz#1004310.  This is a hack,
# but it is needed to make tycho work until this bug is fixed
# properly.
sed -i 's|<maven>|&<extension>zip</extension>|' \
    $RPM_BUILD_ROOT%{_mavendepmapfragdir}/%{name}-zip

%files
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/%{name}
%{_mavendepmapfragdir}/%{name}-zip
%{_javadir}/%{name}/
%doc README.md

%files javadoc
%{_javadocdir}/%{name}

%changelog
* Fri Jun 6 2014 Alexander Kurtakov <akurtako@redhat.com> 0.19.0-5
- Support license feature when creating system repo.

* Thu Nov 21 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-4
- Return expected reactor cache location when XMvn resolution fails.

* Wed Nov 20 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-3
- Bump release for rebuild (Bug 1031769).

* Mon Nov 18 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-2
- Reduce length of file lock name when file is in build directory.

* Thu Oct 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.19.0-1
- Update to 0.19.0 Release.

* Fri Oct 04 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-7
- Do not use XMvn internals (Bug 1015038).

* Thu Oct 3 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.18.1-6
- Adjust to latest Xmvn (workaround for 1015038).

* Mon Sep  9 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.18.1-5
- Add workaround for rhbz#1004310

* Tue Jul 30 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-4
- Improve artifact resolution using XMvn Resolver. (Bug 986900)

* Mon Jul 29 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-3
- Fix Tycho file locking to work in Fedora.
- Skip validateConsistentTychoVersion by default. (Bug 987271)

* Wed Jul 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-2
- Non-bootstrap build.

* Wed Jul 24 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.1-1.1
- Update to use Eclipse Aether.
- Use MavenSession and Plexus to determine state.
- Fix bootstrap build.

* Thu Jul 18 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.1-1
- Make changes to ensure intermediary build succeeds.
- Remove %%Patch6 in favour of call to sed.

* Thu Jul 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.18.1-1
- Update to 0.18.1.

* Tue Jul 16 2013 Roland Grunberg <rgrunber@redhat.com> - 0.18.0-5
- Look for maven artifacts using XMvn Resolver.

* Tue Jul 9 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.0-4
- Update to use maven-surefire 2.15 API.

* Fri Jul 5 2013 Alexander Kurtakov <akurtako@redhat.com> 0.18.0-3
- Use _jnidir too when building local p2 repo.

* Thu Jun 6 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.18.0-2
- Add Requires on plugins present in Maven super POM
- Resolves: rhbz#971301

* Tue May 28 2013 Roland Grunberg <rgrunber@redhat.com> 0.18.0-1
- Update to 0.18.0 Release.

* Thu Apr 11 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-1
- Fix bootstrap build for potential future use.

* Tue Apr 2 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-1
- Update to 0.17.0 Release.

* Mon Mar 18 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.11.git3351b1
- Non-bootstrap build.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.10.git3351b1
- Merge mizdebsk patch with existing custom resolver patch.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.9.git3351b1
- Move the patch into better place.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.8.git3351b1
- Non-bootstrap build.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.7.git3351b1
- Commit the patch.

* Mon Mar 18 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.6.git3351b1
- Use plexus to instantiate workspace reader.

* Sun Mar 17 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.5.git3351b1
- Non-bootstrap build.

* Fri Mar 15 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.4.git3351b1
- Update bootstrapped build for 0.17.0-SNAPSHOT to work against 0.16.0.
- Update to Plexus Compiler 2.2 API.

* Thu Feb 28 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.3.git3351b1
- Update to using Jetty 9 API.

* Mon Feb 25 2013 Roland Grunberg <rgrunber@redhat.com> 0.17.0-0.2.git3351b1
- Set the global default execution environment to JavaSE-1.6.
- Patch clean-up.

* Mon Feb 25 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.17.0-0.1.git3351b1
- Update to latest upstream.
- RHBZ#915194 - API changed in maven-surefire

* Wed Feb 6 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-21
- Non-bootstrap build.

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 0.16.0-20.2
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Feb 6 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-20.1
- Change BR/R on maven to maven-local for XMvn support.
- Build bootstrapped to fix missing Fedora Maven class.

* Thu Jan 24 2013 Roland Grunberg <rgrunber@redhat.com> 0.16.0-20
- Use TYCHO_MVN_{LOCAL,RPMBUILD} to determine how maven was called.
- Update to maven-surefire 2.13.

* Thu Dec 20 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-19
- Fix upstream Bug 361204.

* Mon Dec 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-18
- Add support for more flexible OSGi bundle paths.
- Use OSGi Requires instead of package name.
- Expand Requires to include the Eclipse platform.

* Mon Nov 19 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-17
- Make additional changes to get Tycho building bootstrapped.

* Mon Nov 5 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-16
- Add capability to build without depending on Tycho or Eclipse.

* Sat Oct 20 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-15
- Package org.eclipse.osgi and org.eclipse.jdt.core.

* Fri Oct 19 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-14
- Update to finalized 0.16.0 Release.

* Wed Oct 17 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-13
- Build Tycho properly in one RPM build.
- Update to 0.16.0 Release.

* Thu Oct 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-12.d7f885
- Non-bootstrap build.

* Thu Oct 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-11.1.d7f885
- Remove dependence on eclipse by use of self-bundled equinox launcher.

* Wed Oct 10 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-11.d7f885
- copy-platform-all should make symlinked jars from %%{_javadir} unique.
- Non-bootstrap build (reset the %%bootstrap flag properly).

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-10.d7f885
- Non-bootstrap build.

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-9.1.d7f885
- Filter out OSGi dependencies.

* Thu Oct 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-9.d7f885
- Non-bootstrap build.

* Thu Oct 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-8.1.d7f885
- Fix Bug in overriding of BREE to JavaSE-1.6.

* Wed Oct 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-8.d7f885
- Non-bootstrap build.

* Wed Oct 3 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-7.1.d7f885
- Update to latest 0.16.0 SNAPSHOT.
- First attempts to build without cyclic dependency to JDT.

* Mon Aug 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-7.df2c35
- Non bootstrap-build.

* Mon Aug 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-6.1.df2c35
- Add BR/R on explicit dependency objectweb-asm4.
- Use consistent whitespace in specfile.

* Fri Aug 24 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-6.df2c35
- Non-bootstrap build.

* Thu Aug 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-5.1.df2c35
- Set BREE to at least JavaSE-1.6 for all eclipse packaging types.
- Remove unneeded workaround for JSR14 incompatibility of JDK 1.7.

* Wed Aug 15 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-5.df2c35
- Non-bootstrap build.

* Mon Aug 13 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-4.1.df2c35
- Correctly reference objectweb-asm4 and fix local mode resolution bug.
- Update spec file to honour new java packaging guidelines.

* Thu Aug 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-4.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-3.1.df2c35
- Add tycho.local.keepTarget flag to bypass ignoring environments.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-3.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-2.1.df2c35
- Use recommended %%add_maven_depmap. 

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-2.df2c35
- Non-bootstrap build.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-1.2.df2c35
- Properly change bootstrap flag.
- Add some git ignores.

* Thu Aug 9 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.16.0-1.1.df2c35
- Install missing tycho-standalone-p2-director.zip.

* Thu Aug 2 2012 Roland Grunberg <rgrunber@redhat.com> 0.16.0-1.df2c35
- Update to 0.16.0 SNAPSHOT.

* Tue Jul 31 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-3
- Non-bootstrap build.

* Tue Jul 31 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-2.1
- Ignore defined environments in local mode.

* Mon Jul 30 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-2
- Non-bootstrap build.

* Mon Jul 30 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-1.1
- Fix copy-platform-all script to properly link %%{_datadir}/eclipse jars.

* Thu Jul 26 2012 Roland Grunberg <rgrunber@redhat.com> 0.15.0-1
- Update to 0.15.0.
- Set BREE to at least JavaSE-1.6 for Eclipse feature bundles.

* Wed Jul 25 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-7
- Non-bootstrap build.

* Mon Jul 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-6
- Detect OSGi jars using presence of Bundle-SymbolicName entry (BZ #838513).

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-5
- Non-bootstrap build.

* Tue May 29 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-4.1
- Fix Tycho Surfire to run Eclipse test bundles.
- Implement automatic creation of a system p2 repository.
- Allow building SWT fragments (BZ #380934).

* Wed May 23 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-4
- Non-bootstrap build.

* Thu May 17 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-3.1
- Set BREE to be at least JavaSE-1.6 for Eclipse OSGi bundles.

* Wed May 16 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-3
- Non-bootstrap build.

* Wed Apr 25 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-2.1
- Implement a custom resolver when running in local mode.
- Use upstream solution for BZ #372395 to fix the build.

* Wed Apr 4 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-2
- Non-bootstrap build.

* Tue Mar 27 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-1.1
- Add missing tycho-testing-harness to be packaged.
- Use %%{_eclipse_base} from eclipse-platform.

* Fri Mar 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.1-1
- Update to 0.14.1 upstream tag.
- Allow building against maven-surefire 2.12 (instead of 2.10).
- Stop symlinking o.e.osgi and o.e.jdt.core into the m2 cache.

* Thu Feb 16 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-4
- Non-bootstrap build.

* Tue Feb 14 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-3
- Update to 0.14.0 upstream tag.

* Thu Feb 9 2012 Roland Grunberg <rgrunber@redhat.com> 0.14.0-2
- Non-bootstrap build.

* Wed Feb 01 2012 Roland Grunberg <rgrunber@redhat.com> - 0.14.0-1
- Update to 0.14.0.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri May 27 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.12.0-0.1.a74b1717
- Update to new version do bootstrap from scratch

* Fri May 6 2011 Alexander Kurtakov <akurtako@redhat.com> 0.10.0-3
- Non-bootstrap build.

* Tue May  3 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.10.0-2
- Add README and make build more silent

* Tue Mar 29 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.10.0-1
- First bootstrapped version
