#******************************************************************************
#                                                                             *
#              *    **   *  *   *                           *                 *
#             * *  *  *  *  *  * *                          *                 *
#            ***** *  *  *  * *****  **  ***  *  *  ** ***  ***               *
#            *   * *  *  *  * *   * *  * *  * *  * *   *  * *  *              *
#            *   * *  *  *  * *   * *  * *  * *  *   * *  * *  *              *
#            *   *  ** *  **  *   *  *** ***   *** **  ***  *  *              *
#                                      * *             *                      *
#                                    **  *             *                      *
#                                                                             *
#******************************************************************************
#                                                                             *
#  This file is part of AQUAgpusph, a free CFD program based on SPH.          *
#  Copyright (C) 2012  Jose Luis Cercos Pita <jl.cercos@upm.es>               *
#                                                                             *
#  AQUAgpusph is free software: you can redistribute it and/or modify         *
#  it under the terms of the GNU General Public License as published by       *
#  the Free Software Foundation, either version 3 of the License, or          *
#  (at your option) any later version.                                        *
#                                                                             *
#  AQUAgpusph is distributed in the hope that it will be useful,              *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
#  GNU General Public License for more details.                               *
#                                                                             *
#  You should have received a copy of the GNU General Public License          *
#  along with AQUAgpusph.  If not, see <http://www.gnu.org/licenses/>.        *
#                                                                             *
#******************************************************************************

import sys
import os
from os import path
try:
    from PyQt4 import QtGui
except:
    try:
        from PySide import QtGui
    except:
        raise ImportError("PyQt4 or PySide is required to use this tool")

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
except:
    raise ImportError("matplotlib is required to use this tool")


class FigureController(FigureCanvas):
    """Matplotlib figure widget controller"""

    def __init__(self):
        """Constructor"""
        # Create the figure in the canvas
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        # generates first "empty" plot
        t = [0.0]
        exp_a = [0.0]
        a = [0.0]
        m = [0.0]
        self.exp_line, = self.ax.plot(t,
                                      exp_a,
                                      label=r'$\theta_{Exp}$',
                                      color="black",
                                      linestyle="--",
                                      linewidth=1.0)
        self.line, = self.ax.plot(t,
                                  a,
                                  label=r'$\theta_{SPH}$',
                                  color="black",
                                  linestyle="-",
                                  linewidth=1.0)
        # Set some options
        self.ax.grid()
        self.ax.legend(loc='upper left')
        self.ax.set_xlim(0, 0.1)
        self.ax.set_ylim(-0.1, 0.1)
        self.ax.set_autoscale_on(False)
        self.ax.set_xlabel(r"$t \, [\mathrm{s}]$", fontsize=21)
        self.ax.set_ylabel(r"$\theta \, [\mathrm{deg}]$", fontsize=21)
        # Create a second moment plot
        self.ax2 = self.ax.twinx()
        self.mline, = self.ax2.plot(t,
                                    m,
                                    label=r'$M_{SPH}$',
                                    color="blue",
                                    linewidth=1.0)
        # Set some options
        self.ax2.set_xlim(0, 0.1)
        self.ax2.set_ylim(-0.1, 0.1)
        self.ax2.set_autoscale_on(False)
        self.ax2.set_ylabel(r"$M_{fluid} \, [\mathrm{N} \cdot \mathrm{m}]$",
                            fontsize=21,
                            color="blue")
        for tl in self.ax2.get_yticklabels():
            tl.set_color("blue")
        # force the figure redraw
        self.fig.canvas.draw()
        # call the update method (to speed-up visualization)
        self.timerEvent(None)
        # start timer, trigger event every 1000 millisecs (=1sec)
        self.timer = self.startTimer(1000)

    def readFile(self, filepath):
        """ Read and extract data from a file
        :param filepath File ot read
        """
        abspath = filepath
        if not path.isabs(filepath):
            abspath = path.join(path.dirname(path.abspath(__file__)), filepath)
        # Read the file by lines
        f = open(abspath, "r")
        lines = f.readlines()
        f.close()
        data = []
        for l in lines[:-1]:  # Skip the last line, which may be unready
            l = l.strip()
            fields = l.split('\t')
            try:
                data.append(map(float, fields))
            except:
                continue
        # Transpose the data
        return map(list, zip(*data))

    def timerEvent(self, evt):
        """Custom timerEvent code, called at timer event receive"""
        # Read and plot the new data
        data = self.readFile('Motion.dat')
        t = data[0]
        exp_a = data[2]
        a = data[3]
        m = data[5]
        self.exp_line.set_data(t, exp_a)
        self.line.set_data(t, a)
        self.mline.set_data(t, m)

        self.ax.set_xlim(0, t[-1])
        ymax_exp = max(abs(max(exp_a)), abs(min(exp_a)))
        ymax_sph = max(abs(max(a)), abs(min(a)))
        ymax = max((ymax_exp, ymax_sph))
        self.ax.set_ylim(-1.1 * ymax, 1.1 * ymax)

        self.ax2.set_xlim(0, t[-1])
        ymax = max(abs(max(m)), abs(min(m)))
        self.ax2.set_ylim(-1.1 * ymax, 1.1 * ymax)
        for tl in self.ax2.get_yticklabels():
            tl.set_color("blue")

        # Redraw
        self.fig.canvas.draw()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = FigureController()
    widget.setWindowTitle("Roll angle")
    widget.show()
    sys.exit(app.exec_())
