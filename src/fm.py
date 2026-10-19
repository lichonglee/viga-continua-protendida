import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json
from PIL import Image
F={
'a1':r'y = f\,\left(\frac{x}{c}\right)^{2}',
'a2':r'w_p = \frac{8\,P\,f}{L^{2}}',
'a3':r'p_{bal} = g + \psi_2\,q',
'b1':r"d' = c + \phi_t + \frac{\phi_{bainha}}{2}",
'b2':r"e_{max} = \frac{h}{2} - d'",
'b3':r'e_P = \frac{\sum P_i\,e_i\cos\alpha_i}{\sum P_i\cos\alpha_i}',
'c1':r'e_{lp} \geq \frac{M - \sigma_{lim}\,W}{N} - k',
'c2':r'e_{lp} \leq \frac{M + \sigma_{lim}\,W}{N} + k',
'c3':r'e_{lp} = e - \frac{M_{hip}}{N},\quad k = \frac{W}{A_c}',
'd1':r'P = \frac{p_{bal}\,L^{2}}{8\,f}',
'd2':r'\sigma_{p,j} = 0{,}74\,f_{ptk}',
'd3':r'P_\infty = P_j - \Delta P_{imed} - \Delta P_{prog}',
'e1':r'n \geq \frac{P_\infty}{A_{p1}\,\sigma_{p,\infty}}',
'e2':r'A_p = n_{cab}\,n_{cord}\,A_{p1}',
'e3':r'P_j = A_p\,\sigma_{p,j}',
'g1':r'\sigma_p(x) = \sigma_{p,j}\,e^{-(\mu\,\Sigma\alpha + k\,x)}',
'g2':r'\alpha = \arctan\left(\frac{de}{dx}\right)',
'h1':r'\Delta(x) = \frac{2}{E_p}\left[\int_0^x \sigma\,dx - \sigma(x)\,x\right]',
'h2':r"\sigma'(x) = 2\,\sigma(x_a) - \sigma(x),\quad x \leq x_a",
'h3':r'\Delta\sigma_{ES} = \alpha_p\,\frac{n-1}{2n}\,|\sigma_{cp}|',
'i1':r'\Delta\sigma_p = \frac{|\varepsilon_{cs}|E_p + \alpha_p|\sigma_{cp0g}|\varphi + \sigma_{p0}\chi}{\chi_p + \chi_c\,\alpha_p\,\eta\,\rho_p}',
'i2':r'\chi = -\ln(1-\psi),\quad \psi_\infty = 2{,}5\,\psi_{1000}',
'j1':r'M_{iso} = -P\cos\alpha\;e',
'j2':r'R_B = \frac{6}{L^{3}}\int M_{iso}\,m\,dx',
'j3':r'M_{hip}(x) = -R_B\,m(x),\quad M_P = M_{iso} + M_{hip}',
'k1':r'\sigma_1 = -\frac{N}{A_c} + \frac{M_P + M}{W},\quad \sigma_2 = -\frac{N}{A_c} - \frac{M_P + M}{W}',
'l1':r"y'' = \kappa = -\frac{M}{E_{cs}\,I_c}",
'l2':r'M_{qp} = M_g + \psi_2 M_q + M_{P,\infty}',
'l3':r'\delta_\infty = \delta\,(1+\varphi) \leq \frac{L}{250}',
'm1':r'\varepsilon_{p0} = \frac{\sigma_{p\infty}}{E_p} + \frac{P_\infty}{A_c E_{cs}}\left(1 + \frac{e^{2}A_c}{I_c}\right)',
'm2':r'x = \frac{T_p - C_s}{0{,}85\,f_{cd}\cdot 0{,}8\,b_w}',
'm3':r"M_{Rd} = C_c\,(d_p - 0{,}4x) + C_s\,(d_p - d')",
'n1':r'V_p = -P\sin\alpha,\quad V_{sd} = \gamma_p V_p + 1{,}4\,V_g + 1{,}4\,V_q',
'n2':r'\beta = 1 + \frac{M_0}{M_{sd}} \leq 2,\quad \tau_{c,cor} = \beta\cdot 0{,}6\,f_{ctd}',
'n3':r'\frac{a_{sw}}{n} = \frac{\tau_{wd} - \tau_{c,cor}}{0{,}9\,f_{ywd}}\,b_{w,red}',
'o1':r'\Delta l = \int_0^L \frac{\sigma_p(s)}{E_p}\,ds',
'o2':r'\Delta l \approx \sum \frac{\sigma_i + \sigma_{i+1}}{2}\,\frac{\Delta s}{E_p}',
'o3':r'\Delta l_{liq} = \Delta l - \Delta_{cunha}',
'q1':r'K_{md} = \frac{M_d}{b_w d^{2} f_{cd}},\quad \frac{x}{d} = 1{,}25\left[1 - \sqrt{1 - \frac{2K_{md}}{0{,}85}}\right]',
'q2':r'A_s = \frac{M_d}{f_{yd}\,(d - 0{,}4x)}',
'q3':r'w_k = \frac{\phi}{12{,}5\,\eta_1}\,\frac{\sigma_s}{E_s}\,\frac{3\sigma_s}{f_{ct,m}}',
'r1':r"e_{max} = \frac{h}{2} - d',\quad d' = c + \phi_t + \frac{\phi_{bainha}}{2}",
}
plt.rcParams['mathtext.fontset']='stix'
out={}
for k,t in F.items():
    fig=plt.figure(figsize=(0.1,0.1)); fig.text(0,0,'$'+t+'$',fontsize=40,color='#163F70')
    fig.savefig(f'fm/{k}.png',dpi=200,transparent=True,bbox_inches='tight',pad_inches=0.04); plt.close(fig)
    w,h=Image.open(f'fm/{k}.png').size; out[k]=(w,h)
json.dump(out,open('fm/sizes.json','w')); print({k:(round(v[0]*.3),round(v[1]*.3)) for k,v in out.items()})
