/*******************************************************************************
 * Copyright (c) 2008, 2013 Sonatype Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Sonatype Inc. - initial API and implementation
 *******************************************************************************/
package org.eclipse.tycho.test.multiplatform;

import java.io.File;

import org.apache.maven.it.Verifier;
import org.eclipse.tycho.test.AbstractTychoIntegrationTest;
import org.eclipse.tycho.test.util.ResourceUtil.P2Repositories;
import org.junit.Test;

public class MultiplatformReactorTest extends AbstractTychoIntegrationTest {

    @Test
    public void testMultiplatformReactorBuild() throws Exception {
        Verifier verifier = getVerifier("multiPlatform.reactor", false);
        verifier.getSystemProperties().setProperty("testRepository", P2Repositories.ECLIPSE_342.toString());
        verifier.executeGoal("verify");
        verifier.verifyErrorFreeLog();

        // assert product got proper platform fragments 
        File productTarget = new File(verifier.getBasedir(), "product/target");
        assertFileExists(productTarget, "linux.gtk.x86_64/eclipse/plugins/mpr.fragment.linux_0.0.1.*.jar");
        assertFileExists(productTarget, "win32.win32.x86/eclipse/plugins/mpr.fragment.windows_0.0.1.*.jar");

        // assert site got all platform fragments
        File siteproductTarget = new File(verifier.getBasedir(), "site/target");
        assertFileExists(siteproductTarget, "site/plugins/mpr.fragment.linux_0.0.1.*.jar");
        assertFileExists(siteproductTarget, "site/plugins/mpr.fragment.windows_0.0.1.*.jar");
    }
}
