require 'spec_helper'

describe file('./dummy1.conf') do
  it { should be_file }
end
