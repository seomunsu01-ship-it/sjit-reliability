alter table if exists public.reliability_tests
  add column if not exists cpk_after text;
