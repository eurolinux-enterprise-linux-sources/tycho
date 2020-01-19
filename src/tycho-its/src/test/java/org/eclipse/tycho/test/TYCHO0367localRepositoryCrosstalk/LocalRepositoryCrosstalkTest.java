/*******************************************************************************
 * Copyright (c) 2008, 2011 Sonatype Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Sonatype Inc. - initial API and implementation
 *******************************************************************************/
package org.eclipse.tycho.test.TYCHO0367localRepositoryCrosstalk;

import org.apache.maven.it.Verifier;
import org.eclipse.tycho.test.AbstractTychoIntegrationTest;
import org.eclipse.tycho.test.util.ResourceUtil.P2Repositories;
import org.junit.Test;

public class LocalRepositoryCrosstalkTest extends AbstractTychoIntegrationTest {
    @Test
    public void test() throws Exception {
        // run e352 test first
        Verifier v01 = getVerifier("/TYCHO0367localRepositoryCrosstalk/bundle02", false);
        v01.getSystemProperties().setProperty("p2.repo", P2Repositories.ECLIPSE_352.toString());
        v01.executeGoal("install");
        v01.verifyErrorFreeLog();

        // now run e342 test, it should not "see" e352 artifacts in local repo
        Verifier v02 = getVerifier("/TYCHO0367localRepositoryCrosstalk/bundle01", false);
        v02.getSystemProperties().setProperty("p2.repo", P2Repositories.ECLIPSE_342.toString());
        v02.executeGoal("install");
        v02.verifyErrorFreeLog();
    }

}
