require 'spec_helper'

describe file('./dummy.conf') do
  it { should be_file }
  it { should contain "v1" }
end
