'''
Data from: Srivastav et al. 2016
'''
import snid_runner

# Run SNID:
snid = snid_runner.run_snid('29janflxsc.dat')

print 'Best guess at the type:', snid.select_best_type()
print 'Best estimation of the age: {:.1f}'.format(snid.select_best_age())
print 'Redshift: {:.4f} +-{:.4f} (or +-{:.4f})'.format(*snid.select_best_redshift())
