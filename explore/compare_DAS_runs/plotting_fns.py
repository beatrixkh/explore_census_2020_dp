import matplotlib.pyplot as plt, pandas as pd

def plot_swapping_x_old_v_new(swapping,
                              old_das,
                              new_das,
                              old_label,
                              new_label,
                              title,
                              xlab = '2010 census counts with swapping',
                              ylab = '2010 census counts with DP'):
    x = swapping
    y0 = old_das
    y1 = new_das

    fig = plt.figure() 
    fig.set_size_inches(8,8)

    ax = fig.add_subplot(111)
    ax.scatter(x, y0,
               facecolors='red',
               edgecolors = 'red',
               alpha = 0.25,
               label = old_label)
    ax.scatter(x, y1,
               facecolors='none',
               edgecolors = 'cornflowerblue',
               alpha = 1,
               label = new_label)
    ax.set_aspect('equal', adjustable='box')

    xleft, xright = ax.get_xlim()
    ybottom, ytop = ax.get_ylim()
    lim = max(xright,ytop)
    ax.plot([-1,lim],[-1,lim], 'red', linewidth=1)

    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)

    plt.legend()
    
    return fig


def plot_diff_in_DAS_x_swapping(swapping,
                                old_das,
                                new_das,
                                label = '',
                                title = '',
                                xlab = 'Count size',
                                ylab = 'Difference between new DAS adjustment and old DAS adjustment'):
    
    x = swapping
    y = new_das - old_das

    fig = plt.figure() 
    fig.set_size_inches(8,8)

    ax = fig.add_subplot(111)
    ax.scatter(x, y,
               facecolors='none',
               edgecolors = 'cornflowerblue',
               alpha = 1,
               label = label)

    xleft, xright = ax.get_xlim()
    ybottom, ytop = ax.get_ylim()
    lim = max(xright,ytop)
    ax.plot([0,xright],[0,0], 'red', linewidth=1)

    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)

    plt.legend()


def find_total_error(new, old, sf1):
    
    new_error = new - sf1
    old_error = old - sf1
    
    return pd.DataFrame({'new':[sum(new_error)], 'old':[sum(old_error)]})