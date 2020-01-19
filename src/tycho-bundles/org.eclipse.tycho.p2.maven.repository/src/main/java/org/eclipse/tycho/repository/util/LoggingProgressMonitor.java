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
package org.eclipse.tycho.repository.util;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.tycho.core.facade.MavenLogger;

public class LoggingProgressMonitor implements IProgressMonitor {

    private final MavenLogger logger;

    public LoggingProgressMonitor(MavenLogger logger) {
        this.logger = logger;
    }

    public void beginTask(String name, int totalWork) {
        logger.info(name);
    }

    public void done() {
    }

    public void internalWorked(double work) {
    }

    public boolean isCanceled() {
        return false;
    }

    public void setCanceled(boolean value) {
    }

    public void setTaskName(String name) {
        logger.info(name);
    }

    public void subTask(String name) {
        logger.info(name);
    }

    public void worked(int work) {
    }

}
