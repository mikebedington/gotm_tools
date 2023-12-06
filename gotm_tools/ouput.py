import numpy as np
import datetime as dt
import netCDF4 as nc
import matplotlib
font = {'family' : 'normal',
        'size'   : 16}

matplotlib.rc('font', **font)

from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.pyplot as plt


from functools import *



class gotm_output(object):
    def __init__(self, filename, drop_times=None):
        self.ds = nc.Dataset(filename)
        self._all_vars = list(self.ds.variables)
        self.time_dt = np.asarray([dt.datetime.strptime(this_t.isoformat(), '%Y-%m-%dT%H:%M:%S') for this_t in nc.num2date(self.ds['time'], self.ds['time'].units)])
        self.choose_t = np.ones(len(self.time_dt),dtype=bool)
        if drop_times is not None:
            self.choose_t[0:drop_times] = False

        self.time_dt = self.time_dt[self.choose_t]

        self.dep = np.squeeze(self.ds['z'][self.choose_t,...])
        self.dep_interface = np.squeeze(self.ds['z'][self.choose_t,...])
        self.mean_dep = np.mean(self.dep, axis=0)
        self.mean_dep_interface = np.mean(self.dep_interface, axis=0)

        self.time_2d = np.tile(self.time_dt[:,np.newaxis], [1,self.dep.shape[1]])
        self.time_2d_interface = np.tile(self.time_dt[:,np.newaxis], [1,self.dep_interface.shape[1]])

        self.phyto_class = [] 
        self.zoo_class = []
        
        for this_str in self._all_vars:
            if this_str[0] == 'P' and this_str[-2:] == '_c':
                self.phyto_class.append(this_str.split('_')[0])
            elif this_str[0] == 'Z' and this_str[-2:] == '_c':
                self.zoo_class.append(this_str.split('_')[0])
        
        self.cached_vars = ['total_chl', 'total_zooc', 'total_phytoc']

    def get(self, var):
        if var in self.cached_vars:
            data = getattr(self, var)
        else:
            data = np.squeeze(self.ds[var][self.choose_t,...])
        return data


    @cached_property
    def total_chl(self):
        return np.sum([np.squeeze(self.ds[f'{this_p}_Chl'][self.choose_t,...][np.newaxis,...]) for this_p in self.phyto_class], axis=0) 

    @cached_property
    def total_zooc(self):
        return np.sum([np.squeeze(self.ds[f'{this_z}_c'][self.choose_t,...][np.newaxis,...]) for this_z in self.zoo_class], axis=0)
    
    @cached_property
    def total_phytoc(self):
        return np.sum([np.squeeze(self.ds[f'{this_p}_c'][self.choose_t,...][np.newaxis,...]) for this_p in self.phyto_class], axis=0)


    def quick_plot(self, var, fig=None, ax=None, vmin=None, vmax=None):
        data = self.get(var)    
        
        if data.shape[1] == len(self.mean_dep):
            plot_dep = self.dep
            plot_time = self.time_2d
        else:
            plot_dep = self.dep_interface

        if fig==None:
            fig, ax = plt.subplots(1,1, figsize=[16,16])
            fig.suptitle(var)
            fig.tight_layout()

        if vmin is None:
            vmin = np.min(data)
        if vmax is None:
            vmax = np.max(data)

        pc = ax.pcolormesh(plot_time, plot_dep, data, vmin=vmin, vmax=vmax)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(pc, cax=cax, orientation='vertical')

        return fig, ax

    def quick_surface_plot(self,var):
        data = self.get(var)
        if len(data.shape) == 2:
            data = data[:,-1]
        elif len(data.shape) > 2:
            raise ValueError
        
        fig, ax = plt.subplots(1,1, figsize=[16,10])
        ax.plot(self.time_dt, data)
        fig.suptitle(f'{var} surface values')
        fig.tight_layout()

        return fig, ax

