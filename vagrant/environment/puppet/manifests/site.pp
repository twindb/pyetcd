node /^client$/ {
  include role::client
}

node /^node.*/ {
  include role::etcdnode
}
