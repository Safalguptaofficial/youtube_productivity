#!/usr/bin/env node

// Test script to verify Supabase connection and database schema
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase credentials in .env file');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  console.log('🔍 Testing Supabase connection...');
  console.log(`📍 URL: ${supabaseUrl}`);
  console.log(`🔑 Key: ${supabaseKey.substring(0, 20)}...`);
  console.log('');

  try {
    // Test 1: Basic connection
    console.log('1️⃣ Testing basic connection...');
    const { data, error } = await supabase.from('users').select('count').limit(1);
    
    if (error) {
      console.error('❌ Connection failed:', error.message);
      return false;
    }
    console.log('✅ Connection successful!');
    console.log('');

    // Test 2: Check if tables exist
    console.log('2️⃣ Checking database tables...');
    const tables = ['users', 'videos', 'transcripts', 'summaries', 'jobs'];
    
    for (const table of tables) {
      try {
        const { data, error } = await supabase.from(table).select('*').limit(1);
        if (error) {
          console.log(`❌ Table '${table}' not found or accessible`);
        } else {
          console.log(`✅ Table '${table}' exists and accessible`);
        }
      } catch (err) {
        console.log(`❌ Error checking table '${table}':`, err.message);
      }
    }
    console.log('');

    // Test 3: Check sample data
    console.log('3️⃣ Checking sample data...');
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('*');
    
    if (usersError) {
      console.log('❌ Error fetching users:', usersError.message);
    } else {
      console.log(`✅ Found ${users.length} users in database`);
      users.forEach(user => {
        console.log(`   - ${user.email} (ID: ${user.id})`);
      });
    }
    console.log('');

    // Test 4: Test insert operation
    console.log('4️⃣ Testing insert operation...');
    const testEmail = `test-${Date.now()}@example.com`;
    const { data: newUser, error: insertError } = await supabase
      .from('users')
      .insert([{ email: testEmail }])
      .select();
    
    if (insertError) {
      console.log('❌ Insert test failed:', insertError.message);
    } else {
      console.log('✅ Insert test successful!');
      console.log(`   Created user: ${newUser[0].email}`);
      
      // Clean up test user
      await supabase.from('users').delete().eq('id', newUser[0].id);
      console.log('   Test user cleaned up');
    }
    console.log('');

    // Test 5: Test storage bucket
    console.log('5️⃣ Testing storage bucket...');
    const bucketName = process.env.SUPABASE_BUCKET || 'youtube-productivity-files';
    const { data: buckets, error: bucketError } = await supabase.storage.listBuckets();
    
    if (bucketError) {
      console.log('❌ Error checking storage buckets:', bucketError.message);
    } else {
      const bucket = buckets.find(b => b.name === bucketName);
      if (bucket) {
        console.log(`✅ Storage bucket '${bucketName}' exists`);
        console.log(`   Public: ${bucket.public}`);
      } else {
        console.log(`❌ Storage bucket '${bucketName}' not found`);
        console.log('   Available buckets:', buckets.map(b => b.name).join(', '));
      }
    }

    console.log('');
    console.log('🎉 All tests completed!');
    return true;

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
    return false;
  }
}

// Run the test
testConnection().then(success => {
  process.exit(success ? 0 : 1);
});
