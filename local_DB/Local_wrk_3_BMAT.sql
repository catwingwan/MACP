select decode(worknum_society, 026, 'C-',
      104, 'P-',
      119, 'M-',
      126, 'H-',
      161, 'U-',
      265, 'K-',
      269, 'W-') || worknum worknum, worknum_society, ot_title, e_title, right_type,
       f_get_artist(worknum, worknum_society) performer, f_get_iswc(worknum, worknum_society) ISWC, f_get_wip_name_v2(worknum, worknum_society, p_right_type=>'MEC', p_column=>5) ip_info, distributable
from  (select w.worknum, w.worknum_society, nvl(t.c_title, t.e_title) ot_title, t.e_title, r.distributable, r.right_type
       from   wrk_work w,
              wrk_title t,
              wrk_work_right r
       where  w.worknum = t.worknum
       and    w.worknum_society = t.worknum_society
       and    t.sub_title_id = 0
       and    w.worknum = r.worknum
       and    w.worknum_society = r.worknum_society
       and    r.right_type = 'MEC'
       --and    r.distributable = 'Y'
       and    exists(select 1 from wrk_work_ip_share x, mbr_one_ip_name y, mbr_ip z, mbr_member_header h
                     where  x.worknum = r.worknum
                     and    x.worknum_society = r.worknum_society
                     and    x.right_type = r.right_type
                     and    x.ip_name_no = y.ip_name_no
                     and    y.ip_base_no = z.ip_base_no
                     --and    z.ip_type = 'N' -- writer only
                     and    z.ip_base_no = h.ip_base_no
                    -- and    z.ip_base_no = 'I0001650117' -- publisher
                     and    h.terminate_date is null
                     and    h.joint_date is not null
                    )
      )
union
select decode(worknum_society, 026, 'C-',
      104, 'P-',
      119, 'M-',
      126, 'H-',
      161, 'U-',
      265, 'K-',
      269, 'W-') || worknum worknum, worknum_society, ot_title, e_title, right_type,
       f_get_artist(worknum, worknum_society) performer, f_get_iswc(worknum, worknum_society) ISWC, f_get_wip_name_v2(worknum, worknum_society, p_right_type=>'PER', p_column=>5) ip_info, distributable
from  (select w.worknum, w.worknum_society, nvl(t.c_title, t.e_title) ot_title, t.e_title, r.distributable, r.right_type
       from   wrk_work w,
              wrk_title t,
              wrk_work_right r
       where  w.worknum = t.worknum
       and    w.worknum_society = t.worknum_society
       and    t.sub_title_id = 0
       and    w.worknum = r.worknum
       and    w.worknum_society = r.worknum_society
       and    r.right_type = 'PER'
       --and    r.distributable = 'Y'
       and    exists(select 1 from wrk_work_ip_share x, mbr_one_ip_name y, mbr_ip z, mbr_member_header h
                     where  x.worknum = r.worknum
                     and    x.worknum_society = r.worknum_society
                     and    x.right_type = r.right_type
                     and    x.ip_name_no = y.ip_name_no
                     and    y.ip_base_no = z.ip_base_no
                     --and    z.ip_type = 'N' -- writer only
                     and    z.ip_base_no = h.ip_base_no
                    -- and    z.ip_base_no = 'I0001650117' -- publisher
                     and    h.terminate_date is null
                     and    h.joint_date is not null
                    )
      );