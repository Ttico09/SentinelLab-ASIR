const $ = (id) => document.getElementById(id);
const translations = {repeated_ssh_failures:'Fallos SSH repetidos',ssh_success_after_failures:'Acceso correcto tras intentos fallidos'};
function item(tag, cls, text) { const el=document.createElement(tag); if(cls) el.className=cls; el.textContent=text; return el; }
fetch('report.json').then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(data=>{
  for(const key of ['events','failed','accepted','alerts']) $(key).textContent=data.summary[key];
  $('alert-list').replaceChildren();
  if(!data.alerts.length)$('alert-list').append(item('p','','No se han detectado alertas.'));
  for(const a of data.alerts){
    const box=item('article','alert '+(a.severity==='medium'?'medium':''),'');
    box.append(item('strong','',translations[a.type]||a.type),item('p','',`${a.ip} · ${a.detail}`),item('small','',a.timestamp));
    $('alert-list').append(box);
  }
  $('ip-list').replaceChildren();
  for(const row of data.top_failed_ips){const box=item('div','ip','');box.append(item('code','',row.ip),item('span','',`${row.count} fallos`));$('ip-list').append(box)}
}).catch(err=>{$('alert-list').textContent='No se ha podido cargar report.json. Ejecuta el analizador y abre el panel desde un servidor local. '+err.message});
