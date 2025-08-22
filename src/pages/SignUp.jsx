import React, { useState } from 'react';
import authService from '../appwrite/auth';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../features/userSlice';
import Input from '../components/Input';
import Button from '../components/Button';
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import bgImage from '../assets/bg-image.jpg'; // ✅ import your image

function Signup() {
    const navigate = useNavigate();
    const [error, setError] = useState("");
    const dispatch = useDispatch();
    const { register, handleSubmit } = useForm();

    const create = async (data) => {
        setError("");
        try {
            const account = await authService.createAccount(data);
            if (account) {
                const currentUser = await authService.getCurrentUser();
                if (currentUser) dispatch(login(currentUser));
                navigate("/dashboard");
            }
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div
          className="relative flex items-center justify-center min-h-screen bg-cover bg-center"
          style={{
            backgroundImage: `url(${bgImage})`,
          }}
        >
          {/* Background Overlay (behind form) */}
          <div className="absolute inset-0 bg-[#EEE2D4]/70 z-0"></div>
      
          {/* Decorative Elements */}
          <div className="absolute -top-20 -left-20 w-60 h-60 bg-[#E6D2C0] rounded-full blur-3xl opacity-40 animate-pulse z-0"></div>
          <div className="absolute top-[25%] right-[-5rem] w-72 h-72 bg-[#DCC3A1] rounded-full blur-3xl opacity-30 animate-pulse delay-300 z-0"></div>
          <div className="absolute bottom-20 right-20 w-20 h-20 bg-[#F5DEB3] opacity-40 rounded-full animate-pulse z-0"></div>
          <div className="absolute top-[20%] left-[7%] w-20 h-20 bg-[#C2A37A] opacity-30 rounded-full animate-bounce delay-500 z-0"></div>
          <div className="absolute top-1/2 left-1/3 w-16 h-16 bg-[#C2A37A] opacity-30 rounded-full animate-bounce delay-300 z-0"></div>
          <div className="absolute top-[33%] right-[8%] w-[72px] h-[72px] bg-[#C2A37A] opacity-30 rounded-full animate-bounce delay-200 z-0"></div>
          <div className="absolute bottom-[33%] right-[7%] w-12 h-12 bg-[#C2A37A] opacity-30 rounded-full animate-bounce delay-700 z-0"></div>
          <div className="absolute bottom-[16%] left-[5%] w-20 h-20 bg-[#C2A37A] opacity-30 rounded-full animate-bounce delay-100 z-0"></div>
          <div className="absolute top-1/3 left-1/4 w-2 h-2 bg-white rounded-full opacity-70 animate-ping z-0"></div>
          <div className="absolute bottom-1/3 right-1/3 w-[6px] h-[6px] bg-white rounded-full opacity-60 animate-ping delay-200 z-0"></div>
          <div className="absolute top-1/2 right-1/4 w-2 h-2 bg-white rounded-full opacity-80 animate-ping delay-500 z-0"></div>
          <div className="absolute bottom-10 left-10 w-28 h-28 bg-[#F0D8BE] opacity-40 rounded-[60%_40%_60%_40%] animate-pulse z-0"></div>
      
          {/* Form */}
          <div className="relative z-10 mx-auto w-full max-w-lg bg-[#f6f2ec] rounded-2xl p-10 shadow-lg border border-[#dcd3c4]">
            <h2 className="text-center text-2xl font-bold leading-tight text-[#3b5d42]">
              Sign up to create account
            </h2>
            <p className="mt-2 text-center text-base text-gray-600">
              Already have an account?&nbsp;
              <Link
                to="/login"
                className="font-medium text-[#3b5d42] transition-all duration-200 hover:underline"
              >
                Sign In
              </Link>
            </p>
            {error && <p className="text-red-600 mt-8 text-center">{error}</p>}
      
            <form onSubmit={handleSubmit(create)}>
              <div className="space-y-5">
                <Input
                  label="Full Name:"
                  placeholder="Enter your full name"
                  className="focus:ring-[#3b5d42] focus:border-[#3b5d42]"
                  {...register("name", { required: true })}
                />
                <Input
                  label="Email:"
                  placeholder="Enter your email"
                  type="email"
                  className="focus:ring-[#3b5d42] focus:border-[#3b5d42]"
                  {...register("email", {
                    required: true,
                    validate: {
                      matchPatern: (value) =>
                        /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(value) ||
                        "Email address must be a valid address",
                    },
                  })}
                />
                <Input
                  label="Password:"
                  type="password"
                  placeholder="Enter your password"
                  className="focus:ring-[#3b5d42] focus:border-[#3b5d42]"
                  {...register("password", { required: true })}
                />
                <Button
                  type="submit"
                  className="w-full bg-[#3b5d42] hover:bg-[#2f4c36] text-white rounded-lg transition duration-200"
                >
                  Create Account
                </Button>
              </div>
            </form>
          </div>
        </div>
      );
    }      

export default Signup;
