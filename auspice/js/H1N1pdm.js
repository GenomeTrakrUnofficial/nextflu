var file_prefix = 'H1N1pdm_';
var path = '/data/';
var dfreq_dn = 2;
var tip_labels = true;

var	vaccineChoice = {};
vaccineChoice['A/California/07/2009'] = "2009-09-25";
var vaccineStrains = Object.keys(vaccineChoice);

var epiColorDomain = [0,1,2,3, 4,5,6,7,8,9,10];
var nonEpiColorDomain = [0,1,2,3,4,5,6,7,8,9,10,11];
var rbsColorDomain = [0,0.5, 1,1.5, 2];
var dateDomain = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
var dfreqColorDomain = [-0.27, -0.21, -0.15, -0.09, -0.03, 0.03, 0.09, 0.15, 0.21, 0.27];

var time_ticks = [2010, 2011, 2012, 2013, 2014, 2015];
var	time_window = 2.0;  // layer of one year that is considered current or active
var LBItau = 0.0005;
var LBItime_window = 0.5;
