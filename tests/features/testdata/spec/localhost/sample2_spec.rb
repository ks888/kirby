require 'spec_helper'

describe file('./dummy2.conf') do
  it { should be_file }
end
